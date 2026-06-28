import os
import datetime
from core.services.cloud_bridge import upload_to_gcs

def run_daily_sync():
    # 1. Path to your current production ledger
    # Ensure this path matches where your .db file is actually stored
    ledger_path = "/home/LavetoLab/core/database/laveto_main.db"
    
    if not os.path.exists(ledger_path):
        print(f"Error: Ledger file not found at {ledger_path}")
        return

    # 2. Define the bucket destination with a timestamp
    dest_name = f"backups/ledger_sync_{datetime.date.today()}.db"
    
    # 3. Stream to GCS
    try:
        with open(ledger_path, 'rb') as f:
            upload_to_gcs(f, 'laveto-forensic-bucket', dest_name)
        print(f"System Sync Complete: {dest_name}")
    except Exception as e:
        print(f"Sync Failed: {e}")

if __name__ == "__main__":
    run_daily_sync()