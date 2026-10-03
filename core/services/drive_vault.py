import os
import hashlib
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from core.vault_config import GOOGLE_CREDENTIALS_PATH, SCOPES, DRIVE_FOLDER_ID

def generate_integrity_hash(file_path):
    """Generates a unique SHA-256 fingerprint for the photo to ensure data integrity."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def upload_to_drive(file_path, file_name, vin, member_name, parent_id=None):
    if not DRIVE_FOLDER_ID:
        print("🚨 DRIVE ERROR: DRIVE_FOLDER_ID missing from vault_config!", flush=True)
        return None

    try:
        integrity_hash = generate_integrity_hash(file_path)
        creds = service_account.Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds, cache_discovery=False)

        # Determine target parent (use client-specific folder if provided, else root)
        target_parent = parent_id if parent_id else DRIVE_FOLDER_ID

        file_metadata = {
            'name': f"{vin}_{file_name}",
            'parents': [target_parent]
        }

        media = MediaFileUpload(file_path, mimetype='image/jpeg', resumable=True)

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink',
            supportsAllDrives=True
        ).execute()

        service.permissions().create(
            fileId=file.get('id'),
            body={'role': 'reader', 'type': 'anyone'},
            supportsAllDrives=True
        ).execute()

        return file.get('webViewLink')
    except Exception as e:
        print(f"🚨 DRIVE VAULT ERROR: {e}", flush=True)
        return None

def create_client_vault_matrix(vin, member_name):
    """Forges a structured cloud directory system for a newly enrolled asset cohort."""
    if not DRIVE_FOLDER_ID:
        print("🚨 DRIVE ERROR: DRIVE_FOLDER_ID missing from vault_config!", flush=True)
        return None

    try:
        creds = service_account.Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds, cache_discovery=False)

        # Check if folder already exists to prevent duplicates
        folder_name = f"{vin} — {member_name.upper()}"
        query = f"name = '{folder_name}' and '{DRIVE_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = service.files().list(q=query, fields="files(id)", supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
        
        if results.get('files'):
            return results['files'][0]['id']

        # Forge primary client asset capsule root folder
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [DRIVE_FOLDER_ID]
        }
        parent_folder = service.files().create(
            body=folder_metadata, 
            fields='id',
            supportsAllDrives=True
        ).execute()
        parent_id = parent_folder.get('id')

        # Batch construct decoupled operational archival sub-directories
        subfolders = ["01_Forensic_Evidence", "02_Legal_Covenants", "03_Financial_Settlements"]
        for sub in subfolders:
            sub_metadata = {
                'name': sub,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            service.files().create(
                body=sub_metadata, 
                fields='id',
                supportsAllDrives=True
            ).execute()

        print(f"📡 GOSPEL OS: Google Drive directory maps committed for {vin} // Root ID: {parent_id}", flush=True)
        return parent_id
    except Exception as e:
        print(f"🚨 GOOGLE DRIVE API EXCEPTION: Failed directory mapping operation: {str(e)}", flush=True)
        return None

def delete_client_vault_matrix(drive_folder_id):
    """Permanently purges a client folder matrix from Google Drive upon rejection."""
    if not drive_folder_id:
        return False

    try:
        creds = service_account.Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds, cache_discovery=False)

        print(f"📡 GOSPEL OS: Executing absolute cloud purge for Folder ID: {drive_folder_id}", flush=True)
        service.files().delete(
            fileId=drive_folder_id,
            supportsAllDrives=True
        ).execute()
        return True
    except Exception as e:
        print(f"🚨 GOOGLE DRIVE API PURGE EXCEPTION: Failed to delete directory {drive_folder_id}: {str(e)}", flush=True)
        return False

def get_or_create_pay_ledger_folder(service, folder_name="Laveto_Pay_Ledger", parent_id=None):
    """Ensures a directory exists in the Gospel OS root anchor, returning its ID."""
    target_parent = parent_id if parent_id else DRIVE_FOLDER_ID
    query = f"name = '{folder_name}' and '{target_parent}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(
        q=query,
        fields="files(id, name)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()
    files = results.get('files', [])
    if files:
        return files[0]['id']

    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [target_parent]
    }
    folder = service.files().create(
        body=folder_metadata,
        fields='id',
        supportsAllDrives=True
    ).execute()
    return folder.get('id')


def archive_transaction_to_drive(tx_data, merchant_name="general"):
    """Archives an immutable JSON transaction audit receipt to Gospel OS Google Drive."""
    import json, io
    from googleapiclient.http import MediaIoBaseUpload

    if not DRIVE_FOLDER_ID:
        print("🚨 DRIVE ERROR: DRIVE_FOLDER_ID missing!", flush=True)
        return None
    try:
        creds = service_account.Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds, cache_discovery=False)

        # 1. Get or create root 'Laveto_Pay_Ledger'
        ledger_root_id = get_or_create_pay_ledger_folder(service, "Laveto_Pay_Ledger", DRIVE_FOLDER_ID)

        # 2. Get or create merchant-specific folder
        merchant_folder_id = get_or_create_pay_ledger_folder(service, f"@{merchant_name.lower()}", ledger_root_id)

        # 3. Prepare payload and filename
        ref = tx_data.get('order_ref') or tx_data.get('id') or 'tx'
        file_name = f"RECEIPT_{ref}_{tx_data.get('created_at', '2026')}.json"
        content_bytes = json.dumps(tx_data, indent=2).encode('utf-8')

        media = MediaIoBaseUpload(io.BytesIO(content_bytes), mimetype='application/json', resumable=False)
        file_metadata = {
            'name': file_name,
            'parents': [merchant_folder_id]
        }
        uploaded = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink',
            supportsAllDrives=True
        ).execute()

        print(f"📡 GOSPEL OS: Transaction #{ref} archived to Drive -> {uploaded.get('webViewLink')}", flush=True)
        return uploaded.get('webViewLink')
    except Exception as e:
        print(f"🚨 GOSPEL OS AUDIT UPLOAD ERROR: {e}", flush=True)
        return None
