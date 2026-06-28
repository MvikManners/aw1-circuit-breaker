import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ==========================================
# 🛰️ THE IMMORTALITY PROTOCOL
# ==========================================

# 1. PASTE YOUR FOLDER ID BETWEEN THE QUOTES BELOW
DRIVE_FOLDER_ID = 'PASTE_THAT_LONG_STRING_FROM_STEP_1_HERE'

# 2. VERIFY THE PATH TO YOUR DATABASE
DATABASE_PATH = '/home/LavetoLab/instance/laveto.db' 
KEY_FILE = '/home/LavetoLab/drone_key.json'

def execute_extraction():
    creds = service_account.Credentials.from_service_account_file(KEY_FILE, scopes=['https://www.googleapis.com/auth/drive.file'])
    service = build('drive', 'v3', credentials=creds)
    
    file_metadata = {'name': 'LAVETO_BACKUP.db', 'parents': [DRIVE_FOLDER_ID]}
    media = MediaFileUpload(DATABASE_PATH, mimetype='application/octet-stream')
    
    print("🛰️ Uplinking to Vault...")
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"✅ SUCCESS. File ID: {file.get('id')}")

if __name__ == '__main__':
    execute_extraction()