import os
import sys
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

# Load env vars
load_dotenv(override=True)

server_url = os.getenv("SMTP_SERVER", "smtp.gmail.com")
port = int(os.getenv("SMTP_PORT", "587"))
username = os.getenv("SMTP_USERNAME")
password = os.getenv("SMTP_PASSWORD")
from_email = os.getenv("SMTP_FROM_EMAIL", username)

print(f"Testing SMTP connection to {server_url}:{port} with user {username}...")

msg = EmailMessage()
msg['Subject'] = "DayScore App: Test Email Configuration"
msg['From'] = from_email
msg['To'] = from_email  # Send to self for testing
msg.set_content("If you are reading this, your DayScore email integration works!")

try:
    with smtplib.SMTP(server_url, port) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Failed to send email: {e}")
    sys.exit(1)
