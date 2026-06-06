import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load your email credentials from .env
load_dotenv()


def send_dispute_email(vendor_email, vendor_name, subtotal, tax, grand_total):
    """Sends an automated email to the vendor if calculations are wrong."""

    # If the AI couldn't find an email on the invoice, we can't send a dispute
    if not vendor_email or vendor_email == "":
        return False, "No vendor email found on the invoice."

    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")

    # Calculate what the total SHOULD be
    expected_total = float(subtotal) + float(tax)

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = vendor_email
    msg['Subject'] = "Invoice Discrepancy Notice - Action Required"

    # The body of the email
    body = f"""
    Dear {vendor_name},

    We are processing your recent invoice, but our automated system flagged a calculation error.

    Details extracted from your invoice:
    - Subtotal: ${subtotal}
    - Tax: ${tax}
    - Stated Grand Total: ${grand_total}

    However, our system calculated that Subtotal + Tax equals ${expected_total:.2f}.
    
    Please review your billing system and send a corrected invoice so we can process your payment promptly.

    Regards,
    FinOps Automation System
    """

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to Google's SMTP Server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection
        # Login using your App Password
        server.login(sender_email, sender_password)

        # Send the email!
        server.send_message(msg)
        server.quit()
        return True, f"Dispute email sent to {vendor_email}."
    except Exception as e:
        return False, f"Failed to send email: {e}"
