import hashlib
from database import get_db_connection


def hash_password(password):
    """Converts a plain text password into a secure SHA-256 hash."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username, password, role='User'):
    """Creates a new user in the database. (Useful for initial setup)"""
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed."

    cursor = conn.cursor()
    hashed_pw = hash_password(password)

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
            (username, hashed_pw, role)
        )
        conn.commit()
        return True, f"User '{username}' created successfully as {role}."
    except Exception as e:
        return False, f"Error creating user: {e}"
    finally:
        cursor.close()
        conn.close()


def authenticate_user(username, password):
    """Checks if the username and password match the database."""
    conn = get_db_connection()
    if not conn:
        return None, "Database connection failed."

    cursor = conn.cursor(dictionary=True)
    hashed_pw = hash_password(password)

    try:
        cursor.execute(
            "SELECT id, username, role FROM users WHERE username = %s AND password_hash = %s",
            (username, hashed_pw)
        )
        user = cursor.fetchone()

        if user:
            return user, "Login successful."
        else:
            return None, "Invalid username or password."
    except Exception as e:
        return None, f"Database error: {e}"
    finally:
        cursor.close()
        conn.close()
