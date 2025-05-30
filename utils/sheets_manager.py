from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pandas as pd
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from utils.logger import log_error, log_success

load_dotenv()

class GoogleSheetsManager:
    def __init__(self, credentials_path: str):
        """Initialize with path to service account credentials JSON file."""
        try:
            self.credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets',
                       'https://www.googleapis.com/auth/drive']
            )
            self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
        except Exception as e:
            log_error("Error initializing Google Sheets Manager", e)
            raise

    def create_sheet(self, title: str) -> str:
        """Create a new Google Sheet and return its ID."""
        try:
            spreadsheet = {
                'properties': {
                    'title': title
                }
            }
            spreadsheet = self.sheets_service.spreadsheets().create(body=spreadsheet).execute()
            sheet_id = spreadsheet['spreadsheetId']
            log_success(f"Created sheet with ID: {sheet_id}")
            return sheet_id
        except Exception as e:
            log_error("Error creating sheet", e)
            raise

    def add_data_to_sheet(self, spreadsheet_id: str, data: List[Dict[str, Any]]) -> None:
        """Add data to the specified Google Sheet."""
        try:
            # First verify the sheet exists
            try:
                self.sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            except Exception as e:
                raise ValueError(f"Sheet with ID {spreadsheet_id} does not exist. Create it first using create_sheet().")

            # Convert data to DataFrame
            df = pd.DataFrame(data)
            
            # Convert DataFrame to list of lists
            values = [df.columns.tolist()] + df.values.tolist()
            
            body = {
                'values': values
            }
            
            # Update the sheet
            self.sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='A1',
                valueInputOption='RAW',
                body=body
            ).execute()
            log_success("Added data to sheet")
        except Exception as e:
            log_error("Error adding data to sheet", e)
            raise

    def get_shareable_link(self, spreadsheet_id: str) -> str:
        """Get a shareable link for the Google Sheet."""
        try:
            # First verify the sheet exists
            try:
                self.sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            except Exception as e:
                raise ValueError(f"Sheet with ID {spreadsheet_id} does not exist.")

            # Make the file publicly accessible
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            self.drive_service.permissions().create(
                fileId=spreadsheet_id,
                body=permission
            ).execute()
            
            # Get the web view link
            file = self.drive_service.files().get(
                fileId=spreadsheet_id,
                fields='webViewLink'
            ).execute()
            
            link = file.get('webViewLink')
            log_success(f"Generated shareable link: {link}")
            return link
        except Exception as e:
            log_error("Error getting shareable link", e)
            raise

    def export_as_csv(self, spreadsheet_id: str, output_path: str) -> str:
        """Export the Google Sheet as a CSV file."""
        try:
            # First verify the sheet exists
            try:
                self.sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            except Exception as e:
                raise ValueError(f"Sheet with ID {spreadsheet_id} does not exist.")

            request = self.drive_service.files().export_media(
                fileId=spreadsheet_id,
                mimeType='text/csv'
            )
            
            with open(output_path, 'wb') as f:
                downloader = request.execute()
                f.write(downloader)
            
            log_success(f"Exported sheet as CSV to {output_path}")
            return output_path
        except Exception as e:
            log_error("Error exporting sheet as CSV", e)
            raise

    def export_as_excel(self, spreadsheet_id: str, output_path: str) -> str:
        """Export the Google Sheet as an Excel file."""
        try:
            # First verify the sheet exists
            try:
                self.sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            except Exception as e:
                raise ValueError(f"Sheet with ID {spreadsheet_id} does not exist.")

            request = self.drive_service.files().export_media(
                fileId=spreadsheet_id,
                mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
            with open(output_path, 'wb') as f:
                downloader = request.execute()
                f.write(downloader)
            
            log_success(f"Exported sheet as Excel to {output_path}")
            return output_path
        except Exception as e:
            log_error("Error exporting sheet as Excel", e)
            raise

if __name__ == "__main__":
    # Initialize the manager
    manager = GoogleSheetsManager(os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH"))
    
    # Create a new sheet
    sheet_id = manager.create_sheet("Test Sheet")
    
    # Add some test data
    test_data = [
        {"name": "John Doe", "age": 30},
        {"name": "Jane Smith", "age": 25}
    ]
    manager.add_data_to_sheet(sheet_id, test_data)
    
    # Get shareable link
    link = manager.get_shareable_link(sheet_id)
