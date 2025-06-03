import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Optional
from config import GMAIL_EMAIL, GMAIL_APP_PASSWORD


class GmailSender:
    def __init__(self, email: str, app_password: str):
        """Initialize with Gmail address and app password."""
        self.email = email
        self.app_password = app_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def create_message(
        self,
        sender: str,
        to: str,
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None,
    ) -> MIMEMultipart:
        """Create a message with optional attachments."""
        message = MIMEMultipart()
        message["to"] = to
        message["from"] = sender
        message["subject"] = subject

        # Add body
        msg = MIMEText(body)
        message.attach(msg)

        # Add attachments
        if attachments:
            for file_path in attachments:
                with open(file_path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
                part["Content-Disposition"] = (
                    f'attachment; filename="{os.path.basename(file_path)}"'
                )
                message.attach(part)

        return message

    def send_message(self, message: MIMEMultipart) -> None:
        """Send the message using SMTP."""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.app_password)
                server.send_message(message)
        except Exception as e:
            raise Exception(f"Error sending message: {str(e)}")

    def send_email_with_attachment(
        self,
        sender: str,
        to: str,
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None,
    ) -> None:
        """Send an email with optional attachments."""
        try:
            # Validate inputs
            if not all([sender, to, subject]):
                raise ValueError("Sender, recipient, and subject are required")

            # Ensure body is a string
            if body is None:
                body = ""
            elif isinstance(body, list):
                body = "\n".join(body)

            message = self.create_message(sender, to, subject, body, attachments)
            self.send_message(message)
        except Exception as e:
            raise Exception(f"Failed to send email: {str(e)}")


if __name__ == "__main__":
    sender = GMAIL_EMAIL
    to = "getachewabdulkarim7@gmail.com"
    subject = "Test Email"
    body = "This is a test email"

    # Replace with your Gmail address and app password
    gmail_sender = GmailSender(email=GMAIL_EMAIL, app_password=GMAIL_APP_PASSWORD)
    gmail_sender.send_email_with_attachment(sender, to, subject, body)
