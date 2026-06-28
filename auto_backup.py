import os
import shutil
import tarfile
from datetime import datetime
# Import your existing Drive and the new GCS Bridge
from app import upload_to_drive, app
from core.services.cloud_bridge import upload_to_gcs

def create_full_snapshot(timestamp):
    """Packages the application design DNA."""
    snapshot_name = f"LAVETO_DESIGN_SNAPSHOT_{timestamp}.tar.gz"
    # Directories/Files that define your OS DNA
    sources = ['templates', 'static', 'core', 'app.py', '.env', 'vault_sync.py']
    
    with tarfile.open(snapshot_name, "w:gz") as tar:
        for source in sources:
            if os.path.exists(source):
                tar.add(source)
    return snapshot_name

def run_system_backup():
    print(f"[{datetime.now()}] INITIALIZING MASTER BACKUP...")
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')

    # 1. PATH CONFIGURATION
    db_path = "/home/LavetoLab/laveto.db"
    db_backup_name = f"LAVETO_DB_BACKUP_{timestamp}.db"
    temp_db = f"temp_{db_backup_name}"

    # 2. CAPTURE LEDGER DATA
    if not os.path.exists(db_path):
        print(f"🚨 ERROR: Ledger not found at {db_path}")
        return
    shutil.copy2(db_path, temp_db)

    # 3. CAPTURE DESIGN DNA
    snapshot_name = create_full_snapshot(timestamp)

    try:
        # Define assets to protect
        assets = [(temp_db, db_backup_name), (snapshot_name, snapshot_name)]

        for local_file, remote_name in assets:
            print(f"📡 BEAMING TO CLOUD VAULT: {remote_name}")
            
            # A. Upload to Drive
            upload_to_drive(local_file, remote_name, "SYSTEM_BACKUP", "ARCHITECT_CORE")

            # B. Upload to GCS (Forensic Integrity Vault)
            with open(local_file, 'rb') as f:
                upload_to_gcs(f, 'laveto-forensic-bucket', f'backups/{remote_name}')

        print(f"✅ SUCCESS: Both Ledger and Design DNA secured in Vaults.")

    except Exception as e:
        print(f"🚨 CRITICAL BACKUP ERROR: {str(e)}")

    finally:
        # 4. CLEANUP
        if os.path.exists(temp_db):
            os.remove(temp_db)
        if os.path.exists(snapshot_name):
            os.remove(snapshot_name)
        print("🧹 Local temp files purged.")

if __name__ == "__main__":
    with app.app_context():
        run_system_backup()