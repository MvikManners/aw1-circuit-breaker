# /home/LavetoLab/sync_to_drive.py
# [2026-07-02 12:05:26 CAT] - Master Multi-Target Shared Drive Automation Engine

import os
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# 🛡️ ARCHITECTURAL SYSTEM CONFIGURATION
SERVICE_ACCOUNT_FILE = '/home/LavetoLab/google_key.json'
SCOPES = ['https://www.googleapis.com/auth/drive']
LOCAL_BACKUP_DIR = '/home/LavetoLab/backups/'

# 🏛️ MASTER SHARED DRIVE COMPARTMENT MATRIX (UNIFIED MAP)
RECYCLE_BIN_ID = '1vePLHBswT9sc3FTgs6MeUOX13P-qXVcQ'

DRIVE_COMPARTMENTS = {
    'LAVETO_MASTER_BACKUPS': {
        'id': '1ZGyXj5EQ1KbtkhEphlO2ghLTvv3mfmFk',
        'limit': 7,          
        'extensions': ['.db', '.zip.enc']
    },
    'ARCHITECT_CORE': {
        'id': '1f9_ARCHITECT_CORE_ID_HERE', # Fallback matching name block
        'limit': 5,
        'extensions': ['.tar.gz', '.bak']
    },
    '04_SYSTEM_ARCHITECTURE': {
        'id': '1f9_SYSTEM_ARCH_ID_HERE',
        'limit': 14,
        'extensions': ['.py', '.yml', '.conf']
    },
    '03_MEMBER_REGISTRY': {
        'id': '1f9_MEMBER_REG_ID_HERE',
        'limit': 30,
        'extensions': ['.json', '.csv']
    },
    '02_TREASURY_AND_AUDIT': {
        'id': '1f9_TREASURY_AUDIT_ID_HERE',
        'limit': 30,
        'extensions': ['.xlsx', '.pdf']
    },
    '01_FIELD_OPERATIONS': {
        'id': '1f9_FIELD_OPS_ID_HERE',
        'limit': 50,
        'extensions': ['.jpg', '.jpeg', '.png', '.mp4']
    }
}

def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def sync_all_compartments():
    service = get_drive_service()
    print("====================================================")
    print(f"⏰ AUTOMATION SEQUENCE START: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} CAT")
    print("====================================================")

    # 1. TRANSMIT AND PURGE MATCHING LOCAL BINARIES
    if os.path.exists(LOCAL_BACKUP_DIR):
        local_files = os.listdir(LOCAL_BACKUP_DIR)
        for filename in local_files:
            file_path = os.path.join(LOCAL_BACKUP_DIR, filename)
            
            target_folder_id = None
            for comp_name, config in DRIVE_COMPARTMENTS.items():
                if any(filename.lower().endswith(ext) for ext in config['extensions']):
                    if "YOUR_" not in config['id'] and "ID_HERE" not in config['id']: 
                        target_folder_id = config['id']
                        break
            
            if target_folder_id:
                try:
                    file_metadata = {'name': filename, 'parents': [target_folder_id]}
                    media = MediaFileUpload(file_path, mimetype='application/octet-stream', resumable=True)
                    print(f"📡 Uploading local asset -> {filename}")
                    
                    file = service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id',
                        supportsAllDrives=True
                    ).execute()
                    
                    if file.get('id'):
                        os.remove(file_path)
                        print(f"✅ Local Node Cleared: {filename}")
                except Exception as ex:
                    print(f"⚠️ Transmission error for {filename}: {ex}")

    # 2. RUN REMOTE RETENTION CLEANUP LOOPS ACROSS ALL COMPARTMENTS
    for comp_name, config in DRIVE_COMPARTMENTS.items():
        folder_id = config['id']
        ceiling = config['limit']
        
        if "YOUR_" in folder_id or "ID_HERE" in folder_id:
            print(f"ℹ️ Compartment {comp_name} bypass: Awaiting link ID mapping string.")
            continue
            
        try:
            print(f"\n🔒 Scanning capacity limits for directory: {comp_name}...")
            results = service.files().list(
                q=f"'{folder_id}' in parents and trashed = false",
                fields="files(id, name)",
                orderBy="name desc",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute()
            
            remote_files = results.get('files', [])
            print(f"📊 Live counts: {len(remote_files)} / Capacity Ceiling: {ceiling}")
            
            if len(remote_files) > ceiling:
                overflow = remote_files[ceiling:]
                print(f"✂️ Overlap identified: Shifting {len(overflow)} items to Recycle Node...")
                
                for stale_file in overflow:
                    fid = stale_file['id']
                    fname = stale_file['name']
                    try:
                        service.files().update(
                            fileId=fid,
                            addParents=RECYCLE_BIN_ID,
                            removeParents=folder_id,
                            fields='id',
                            supportsAllDrives=True
                        ).execute()
                        print(f"📦 Shifted successfully: {fname}")
                    except Exception as loop_ex:
                        print(f"⚠️ Shifting block fault for {fname}: {loop_ex}")
            else:
                print(f"🟢 Storage profile optimized: {comp_name} is stable.")
                
        except Exception as comp_ex:
            print(f"🚨 Scan error on compartment {comp_name}: {comp_ex}")

    print("\n====================================================")
    print("🏁 SYSTEM AUTOMATION RUN END: Registry Fully Unified.")
    print("====================================================")

if __name__ == "__main__":
    sync_all_compartments()
