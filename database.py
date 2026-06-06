import mysql.connector
import os
from dotenv import load_dotenv

# Load secrets from .env file
load_dotenv()


def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None


def initialize_database():
    """Creates the 3 core tables if they do not exist."""

    # First, connect without a database to create the DB itself if needed
    temp_conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    temp_cursor = temp_conn.cursor()
    temp_cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')}")
    temp_conn.close()

    # Now connect to the specific database
    conn = get_db_connection()
    if conn is None:
        return

    cursor = conn.cursor()

    # 1. Create USERS Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role ENUM('Admin', 'User') DEFAULT 'User'
        )
    """)

    # 2. Create INVOICES Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            file_hash VARCHAR(32) UNIQUE NOT NULL,
            vendor_name VARCHAR(100),
            vendor_email VARCHAR(150),
            grand_total DECIMAL(10,2),
            status VARCHAR(50) DEFAULT 'Pending',
            uploaded_by INT,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (uploaded_by) REFERENCES users(id)
        )
    """)

    # 3. Create AUDIT_LOGS Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            action VARCHAR(255) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Database and Tables initialized successfully!")


# Run this once to set up the database
if __name__ == "__main__":
    initialize_database()
