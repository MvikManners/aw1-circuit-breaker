# /home/LavetoLab/sync_to_drive.py
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = '/home/LavetoLab/credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive.file']
BACKUP_DIR = '/home/LavetoLab/backups/'
FOLDER_ID = 'PASTE_YOUR_FOLDER_ID_HERE' 

def sync_backups():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    files_to_sync = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".zip.enc")]
    
    if not files_to_sync:
        print("No new backups to sync.")
        return

    for filename in files_to_sync:
        file_path = os.path.join(BACKUP_DIR, filename)
        file_metadata = {'name': filename, 'parents': [FOLDER_ID]}
        media = MediaFileUpload(file_path, mimetype='application/octet-stream')
        
        try:
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            if file.get('id'):
                os.remove(file_path)
                print(f"✅ Migrated and Purged: {filename}")
        except Exception as e:
            print(f"❌ Failed to sync {filename}: {e}")

if __name__ == "__main__":
    sync_backups()