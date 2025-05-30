import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from typing import List, Optional

class GmailSender:
    def __init__(self, credentials_path: str, token_path: str):
        """Initialize with paths to credentials and token files."""
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = self._get_gmail_service()

    def _get_gmail_service(self):
        """Get or create Gmail service with proper authentication."""
        creds = None
        
        # Load token if it exists
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If credentials are invalid or don't exist, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path,
                    ['https://www.googleapis.com/auth/gmail.send']
                )
                creds = flow.run_local_server(port=0)
            
            # Save the credentials
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return build('gmail', 'v1', credentials=creds)

    def create_message(self, sender: str, to: str, subject: str, 
                      body: str, attachments: Optional[List[str]] = None) -> dict:
        """Create a message with optional attachments."""
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject

        # Add body
        msg = MIMEText(body)
        message.attach(msg)

        # Add attachments
        if attachments:
            for file_path in attachments:
                with open(file_path, 'rb') as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                message.attach(part)

        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}

    def send_message(self, message: dict) -> dict:
        """Send the message."""
        try:
            message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            return message
        except Exception as e:
            raise Exception(f"Error sending message: {str(e)}")

    def send_email_with_attachment(self, sender: str, to: str, subject: str, 
                                 body: str, attachments: Optional[List[str]] = None) -> dict:
        """Send an email with optional attachments."""
        message = self.create_message(sender, to, subject, body, attachments)
        return self.send_message(message) 