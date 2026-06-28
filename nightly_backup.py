import os
import subprocess
from datetime import datetime
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

# 🛑 WELD 1: Import your secure Drive connection from your main app
from app import get_drive_service, PARENT_FOLDER_ID

BACKUP_FOLDER_NAME = 'LAVETO_MASTER_BACKUPS'

def execute_nightly_backup():
    print(f"🛡️ Starting Gospel OS Master Backup: {datetime.utcnow()}")

    # 1. READ THE VAULT: Get the secure MySQL password from your .env file
    env_path = '/home/LavetoLab/.env'
    load_dotenv(env_path)
    db_password = os.environ.get('DB_PASSWORD')

    if not db_password:
        print("🚨 FATAL: Could not find DB_PASSWORD in .env file! Backup aborted.")
        return

    # 2. FORGE THE CLONE: Create a timestamped MySQL database snapshot
    timestamp = datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
    backup_filename = f"GOSPEL_OS_MYSQL_BACKUP_{timestamp}.sql"

    print("⚙️ Executing MySQL Dump...")
    db_user = "LavetoLab"
    db_host = "LavetoLab.mysql.pythonanywhere-services.com"
    db_name = "LavetoLab$gospel_os"

    # The command that safely extracts your live database
    dump_command = f"mysqldump -u {db_user} -h {db_host} -p'{db_password}' {db_name} > {backup_filename}"

    try:
        # Run the extraction
        subprocess.run(dump_command, shell=True, check=True)
        print(f"✅ SUCCESS: Live database extracted to {backup_filename}")
    except subprocess.CalledProcessError as e:
        print(f"🚨 FATAL: MySQL dump failed! {e}")
        return

    # 3. UPLOAD PROTOCOL: Transmit to Google Drive
    try:
        service = get_drive_service()

        # Locate or Create the Master Backups Folder in the Shared Drive
        query = f"name='{BACKUP_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and '{PARENT_FOLDER_ID}' in parents and trashed=false"
        results = service.files().list(q=query, fields="files(id)", supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
        folders = results.get('files', [])

        if folders:
            backup_folder_id = folders[0]['id']
        else:
            folder_metadata = {
                'name': BACKUP_FOLDER_NAME,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [PARENT_FOLDER_ID]
            }
            folder = service.files().create(body=folder_metadata, fields='id', supportsAllDrives=True).execute()
            backup_folder_id = folder.get('id')

        # Direct Payload Injection to the Workspace Vault
        file_metadata = {'name': backup_filename, 'parents': [backup_folder_id]}
        media = MediaFileUpload(backup_filename, mimetype='application/sql', resumable=False)

        service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True
        ).execute()

        print(f"✅ SUCCESS: {backup_filename} secured in Google Drive.")

        # 🛑 WELD 3: THE HEARTBEAT SENSOR
        # This writes the pulse file so the Command Wall knows the backup succeeded
        with open("/home/LavetoLab/last_backup_heartbeat.txt", "w") as f:
            f.write(str(datetime.now()))
        print("💓 Heartbeat logged successfully. System stability confirmed.")

    except Exception as e:
        print(f"🚨 BACKUP UPLOAD ERROR: {e}")

    finally:
        # 4. BURN THE EVIDENCE: Destroy the temporary local clone to save server space
        if os.path.exists(backup_filename):
            os.remove(backup_filename)

            # Add this at the end of nightly_backup.py
import subprocess
subprocess.run(["python3", "/home/LavetoLab/sync_to_drive.py"])

if __name__ == '__main__':
    execute_nightly_backup()