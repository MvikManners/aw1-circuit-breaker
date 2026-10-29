import os
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 🛡️ SOVEREIGN DRIVE CONFIG (WIRED)
SCOPES = ['https://www.googleapis.com/auth/drive']

# 🤖 BOT: ledger-backup-bot@gospel-os-fortress.iam.gserviceaccount.com
SERVICE_ACCOUNT_FILE = '/home/LavetoLab/credentials.json'

# 📂 TARGET: The shared "LAVETO" folder
PARENT_FOLDER_ID = '1ZGyXj5EQ1KbtkhEphlO2ghLTvv3mfmFk'

def get_drive_service():
    """Connects using the Gospel OS Fortress Bot."""
    try:
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            print(f"🚨 CRITICAL: {SERVICE_ACCOUNT_FILE} not found!")
            return None
            
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        return build('drive', 'v3', credentials=creds, cache_discovery=False)
    except Exception as e:
        print(f"🚨 DRIVE AUTH ERROR: {e}")
        return None

def sync_report_to_drive(vin_dna, local_file_path, file_name):
    """Archives the vehicle forensic PDF in the cloud vault."""
    try:
        # ⏳ Verify the local file exists first
        if not os.path.exists(local_file_path):
            print(f"❌ LOCAL FILE MISSING: {local_file_path}")
            return False

        service = get_drive_service()
        if not service: return False

        # 1. Search for existing ASSET folder for this VIN
        query = f"name = 'ASSET_{vin_dna}' and mimeType = 'application/vnd.google-apps.folder' and '{PARENT_FOLDER_ID}' in parents and trashed = false"
        results = service.files().list(
            q=query, 
            fields="files(id)",
            supportsAllDrives=True, 
            includeItemsFromAllDrives=True
        ).execute()
        
        folders = results.get('files', [])

        if folders:
            folder_id = folders[0]['id']
        else:
            # Create new folder if it's the first report for this car
            folder_metadata = {
                'name': f"ASSET_{vin_dna}",
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [PARENT_FOLDER_ID]
            }
            folder = service.files().create(
                body=folder_metadata, 
                fields='id',
                supportsAllDrives=True
            ).execute()
            folder_id = folder.get('id')

        # 2. Upload the PDF
        file_metadata = {'name': file_name, 'parents': [folder_id]}
        media = MediaFileUpload(local_file_path, mimetype='application/pdf', resumable=True)
        
        uploaded_file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id, webViewLink',
            supportsAllDrives=True
        ).execute()

        # 3. Grant "Anyone with link" read access so it shows up in the Client Vault
        service.permissions().create(
            fileId=uploaded_file.get('id'),
            body={'type': 'anyone', 'role': 'reader'},
            supportsAllDrives=True
        ).execute()

        print(f"✅ DRIVE SYNC SUCCESS: {file_name} is secured in ASSET_{vin_dna}")
        return True

    except Exception as e:
        print(f"⚠️ CLOUD UPLINK FAILED: {e}")
        return False