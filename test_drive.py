import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# CONFIG - Matches your drive_handler.py
SERVICE_ACCOUNT_FILE = '/home/LavetoLab/credentials.json'
PARENT_FOLDER_ID = '1ZGyXj5EQ1KbtkhEphlO2ghLTvv3mfmFk'
SCOPES = ['https://www.googleapis.com/auth/drive']

def test_connection():
    print("🛰️ Starting Connection Test...")
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
        
        # Action: Try to create a "Connection Test" folder
        file_metadata = {
            'name': 'LAVETO_CONNECTION_SUCCESS',
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [PARENT_FOLDER_ID]
        }
        
        print("📡 Attempting to create a test folder in Google Drive...")
        folder = service.files().create(body=file_metadata, fields='id', supportsAllDrives=True).execute()
        
        print(f"✅ SUCCESS! Created Folder ID: {folder.get('id')}")
        print("🚀 Your bot is officially wired to Google Drive.")

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        print("\nPossible fixes:")
        print("1. Did you Share the Google folder with ledger-backup-bot@gospel-os-fortress.iam.gserviceaccount.com?")
        print("2. Is your credentials.json file saved and complete?")

if __name__ == "__main__":
    test_connection()