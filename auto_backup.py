# ===================================================================
# 🛡️ LAVETO GOSPEL OS - UPDATED DUAL-PAYLOAD BACKUP ENGINE
# ===================================================================
import os
import sys
import shutil
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# Target Parent Folder ID
DRIVE_FOLDER_ID = '1ZGyXj5EQ1KbtkhEphlO2ghLTvv3mfmFk' 

def upload_to_drive(file_path, folder_id, label="NODE"):
    """Streams system assets to the Shared Drive Hub."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Target system node absent: {file_path}")

    creds = service_account.Credentials.from_service_account_file('/home/LavetoLab/google_key.json')
    service = build('drive', 'v3', credentials=creds)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    base_name = os.path.basename(file_path)
    backup_filename = f"{label}_{timestamp}_{base_name}"

    file_metadata = {'name': backup_filename, 'parents': [folder_id]}
    media = MediaFileUpload(file_path, mimetype='application/octet-stream', resumable=True)
    
    print(f"📡 Transmitting {label} payload: {backup_filename}")
    
    file = service.files().create(
        body=file_metadata, 
        media_body=media, 
        fields='id',
        supportsAllDrives=True
    ).execute()
    
    return file.get('id')

if __name__ == "__main__":
    # Define production assets
    db_node = "/home/LavetoLab/app.db"
    templates_node = "/home/LavetoLab/templates"
    
    try:
        print("====================================================")
        print(f"⏰ TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} CAT")
        print(f"🔒 INITIALIZING FULL LEDGER SNAPSHOT...")
        
        # STAGE 1: Upload Database
        db_id = upload_to_drive(db_node, DRIVE_FOLDER_ID, label="DB_LEDGER")
        
        # STAGE 2: Compress and Upload Templates
        temp_zip = "/tmp/templates_backup.zip"
        shutil.make_archive("/tmp/templates_backup", 'zip', templates_node)
        temp_id = upload_to_drive(temp_zip, DRIVE_FOLDER_ID, label="UI_TEMPLATES")
        
        print(f"✅ VAULT RECONCILIATION SUCCESSFUL.")
        print(f"📦 DB RECORD // ID: {db_id}")
        print(f"📦 UI RECORD // ID: {temp_id}")
        print("====================================================")
        sys.exit(0)
    except Exception as e:
        print(f"🚨 BACKEND INTEGRATION FAULT: {str(e)}")
        print("====================================================")
        sys.exit(1)