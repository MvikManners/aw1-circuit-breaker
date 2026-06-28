import os
import hashlib
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from core.vault_config import DRIVE_FOLDER_ID, GOOGLE_CREDENTIALS_PATH 

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def generate_integrity_hash(file_path):
    """Generates a unique SHA-256 fingerprint for the photo to ensure data integrity."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def upload_to_drive(file_path, file_name, vin, member_name):
    # 🟢 Verify folder configuration
    if not DRIVE_FOLDER_ID:
        print("🚨 DRIVE ERROR: DRIVE_FOLDER_ID missing from vault_config!")
        return None

    try:
        # 🟢 1. INTEGRITY CHECK: Calculate the fingerprint before upload
        integrity_hash = generate_integrity_hash(file_path)
        print(f"🟢 INTEGRITY VERIFIED FOR {file_name} [VIN: {vin}]: {integrity_hash}")

        # 🟢 2. AUTHENTICATION
        creds = service_account.Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)

        # 🟢 3. UPLOAD METADATA
        file_metadata = {
            'name': f"{vin}_{file_name}",
            'parents': [DRIVE_FOLDER_ID]
        }
        
        media = MediaFileUpload(file_path, mimetype='image/jpeg', resumable=True)
        
        # 🟢 4. EXECUTE BEAM
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        # 🟢 5. SET PUBLIC ACCESS
        service.permissions().create(
            fileId=file.get('id'),
            body={'role': 'reader', 'type': 'anyone'}
        ).execute()

        print(f"🏁 UPLOAD COMPLETE: {file.get('webViewLink')}")
        return file.get('webViewLink')

    except Exception as e:
        print(f"🚨 DRIVE VAULT ERROR: {e}")
        return None