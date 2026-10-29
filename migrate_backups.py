import os
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

SERVICE_ACCOUNT_FILE = '/home/LavetoLab/credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive.file']
BACKUP_DIR = '/home/LavetoLab/backups/'
FOLDER_ID = '1ZGyXj5EQ1KbtkhEphlO2ghLTvv3mfmFk' 

def sync_and_purge():
    # Authenticate
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    # Check for files
    if not os.path.exists(BACKUP_DIR):
        print(f"Directory {BACKUP_DIR} does not exist.")
        return

    for filename in os.listdir(BACKUP_DIR):
        if filename.endswith(".zip.enc"):
            file_path = os.path.join(BACKUP_DIR, filename)
            
            # Prepare upload
            file_metadata = {'name': filename, 'parents': [FOLDER_ID]}
            media = MediaFileUpload(file_path, mimetype='application/octet-stream')
            
            try:
                # Upload with supportsAllDrives=True to bridge to Shared Drive
                service.files().create(
                    body=file_metadata, 
                    media_body=media, 
                    supportsAllDrives=True
                ).execute()
                
                # Verify and Purge
                os.remove(file_path)
                print(f"✅ Transmitted and purged: {filename}")
                
            except Exception as e:
                print(f"❌ Transmission failed for {filename}: {e}")

if __name__ == "__main__":
    sync_and_purge()