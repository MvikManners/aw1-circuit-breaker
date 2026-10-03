import os
import shutil
import time
import logging
import zipfile
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# 📂 CONFIGURATION & SYSTEM ROOTS
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

DB_PATH = os.path.join(BASE_DIR, 'instance', 'gospel_v4.db')
CORE_DIR = os.path.join(BASE_DIR, 'core')
UPLOAD_DIR = os.path.join(BASE_DIR, 'static')
ENV_PATH = os.path.join(BASE_DIR, '.env')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'vault_sync.log')

os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

SECRET_KEY = os.environ.get('BACKUP_ENCRYPTION_KEY')
if SECRET_KEY:
    SECRET_KEY = SECRET_KEY.encode()
else:
    logging.critical("🚨 CRITICAL: BACKUP_ENCRYPTION_KEY absent from environment.")
    raise EnvironmentError("Missing BACKUP_ENCRYPTION_KEY")

def purge_old_backups(days=7):
    """Slashes archives older than the specified retention window."""
    now = time.time()
    for f in os.listdir(BACKUP_DIR):
        f_path = os.path.join(BACKUP_DIR, f)
        if os.stat(f_path).st_mtime < now - (days * 86400):
            if os.path.isfile(f_path):
                os.remove(f_path)
                logging.info(f"🗑️ Purged stale storage node: {f}")

def execute_vault_sync():
    timestamp = time.strftime("%Y-%m-%d_%H%M%S")
    archive_zip = os.path.join(BACKUP_DIR, f"ledger_{timestamp}.zip")
    archive_enc = f"{archive_zip}.enc"
    
    try:
        # 1. SURGICAL PACKAGING NODE: Build complete code + state archive
        print(f"📦 Compiling unified system blueprint: ledger_{timestamp}...", flush=True)
        with zipfile.ZipFile(archive_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            
            # A. Pack the entire Python backend codebase tree
            if os.path.exists(CORE_DIR):
                for root, dirs, files in os.walk(CORE_DIR):
                    for file in files:
                        if '__pycache__' not in root:
                            file_abs = os.path.join(root, file)
                            file_rel = os.path.relpath(file_abs, BASE_DIR)
                            zipf.write(file_abs, file_rel)
            
            # B. Pack the core database state layer
            if os.path.exists(DB_PATH):
                zipf.write(DB_PATH, os.path.relpath(DB_PATH, BASE_DIR))
                
            # C. Pack environment configuration properties
            if os.path.exists(ENV_PATH):
                zipf.write(ENV_PATH, os.path.relpath(ENV_PATH, BASE_DIR))

            # D. Pack asset binaries and media uploads
            if os.path.exists(UPLOAD_DIR):
                for root, dirs, files in os.walk(UPLOAD_DIR):
                    for file in files:
                        file_abs = os.path.join(root, file)
                        file_rel = os.path.relpath(file_abs, BASE_DIR)
                        zipf.write(file_abs, file_rel)

        # 2. CRYPTO LOCK PROTOCOL
        cipher_suite = Fernet(SECRET_KEY)
        with open(archive_zip, 'rb') as file:
            encrypted_data = cipher_suite.encrypt(file.read())
            
        with open(archive_enc, 'wb') as file:
            file.write(encrypted_data)
            
        if os.path.exists(archive_zip):
            os.remove(archive_zip)
            
        logging.info(f"✅ Full System Backup Consolidated: ledger_{timestamp}.zip.enc [Code + Data Staged]")
        print(f"✅ ARCHIVE SECURED: Source code and data pools unified successfully.", flush=True)
        
        purge_old_backups(days=7)
    except Exception as e:
        logging.error(f"🚨 Vault Sync Engine Fault: {e}")
        print(f"🚨 RUNTIME FAULT: Backup routine failed -> {e}", flush=True)

if __name__ == "__main__":
    logging.info("🚀 Master Backend + State Daemon initialized.")
    while True:
        execute_vault_sync()
        time.sleep(300)
