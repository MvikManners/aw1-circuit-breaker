import os
import shutil
import time
import logging
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 📂 CONFIGURATION & ENV LOADING
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Explicitly load the .env file from the home directory
load_dotenv(os.path.join(BASE_DIR, '.env'))

DB_PATH = os.path.join(BASE_DIR, 'instance', 'gospel_v4.db')
UPLOAD_DIR = os.path.join(BASE_DIR, 'static')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'vault_sync.log')

# Ensure directories exist
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Pull key from .env; fallback provided for safety, though .env is now priority
SECRET_KEY = os.environ.get('BACKUP_ENCRYPTION_KEY')
if SECRET_KEY:
    SECRET_KEY = SECRET_KEY.encode()
else:
    # Log a critical warning if key is missing
    logging.critical("🚨 BACKUP_ENCRYPTION_KEY not found in .env file!")
    raise EnvironmentError("Missing BACKUP_ENCRYPTION_KEY")

def purge_old_backups(days=7):
    """Deletes backups older than the specified number of days."""
    now = time.time()
    for f in os.listdir(BACKUP_DIR):
        f_path = os.path.join(BACKUP_DIR, f)
        if os.stat(f_path).st_mtime < now - (days * 86400):
            if os.path.isfile(f_path):
                os.remove(f_path)
                logging.info(f"🗑️ Purged old backup: {f}")

def execute_vault_sync():
    timestamp = time.strftime("%Y-%m-%d_%H%M%S")
    archive_name = os.path.join(BACKUP_DIR, f"ledger_{timestamp}")
    
    try:
        # 1. Compress
        temp_db_path = os.path.join(UPLOAD_DIR, 'gospel_v4.db')
        shutil.copy2(DB_PATH, temp_db_path)
        shutil.make_archive(archive_name, 'zip', UPLOAD_DIR)
        os.remove(temp_db_path)

        # 2. Encrypt
        cipher_suite = Fernet(SECRET_KEY)
        with open(f"{archive_name}.zip", 'rb') as file:
            encrypted_data = cipher_suite.encrypt(file.read())
        with open(f"{archive_name}.zip.enc", 'wb') as file:
            file.write(encrypted_data)
        os.remove(f"{archive_name}.zip")
        
        logging.info(f"✅ Vault Sync Complete: ledger_{timestamp}.zip.enc")
        
        # 3. Purge old files
        purge_old_backups(days=7)

    except Exception as e:
        logging.error(f"🚨 Vault Sync Failed: {e}")

if __name__ == "__main__":
    logging.info("🚀 Forensic Sync Daemon initiated with Purge logic and .env integration.")
    while True:
        execute_vault_sync()
        time.sleep(300) # 5-minute interval