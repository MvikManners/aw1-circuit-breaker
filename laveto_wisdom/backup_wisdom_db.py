"""
Automated Database Backup & Maintenance Utility for Laveto Wisdom AW.
Creates safe SQLite online backups and prunes telemetry logs older than 90 days.
"""
import os
import sqlite3
from datetime import datetime

SRC_DB = "/home/LavetoLab/lvt_backend/lvt_database.db"
BACKUP_DIR = "/home/LavetoLab/lvt_backend/backups"

def run_backup():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    dest_file = os.path.join(BACKUP_DIR, f"lvt_database_backup_{timestamp}.db")

    print(f"Starting online SQLite backup to: {dest_file}")
    
    src_conn = sqlite3.connect(SRC_DB)
    dest_conn = sqlite3.connect(dest_file)
    
    # Online atomic backup (prevents locking live web requests)
    with dest_conn:
        src_conn.backup(dest_conn, pages=250)
        
    dest_conn.close()
    
    # Prune telemetry older than 90 days
    with src_conn:
        deleted = src_conn.execute(
            "DELETE FROM wisdom_api_usage WHERE timestamp < datetime('now', '-90 days')"
        ).rowcount
        print(f"Pruned {deleted} expired telemetry rows (>90 days).")
        
    src_conn.close()
    
    # Retain only the last 7 backup files
    all_backups = sorted([os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.startswith("lvt_database_backup_")])
    if len(all_backups) > 7:
        for old in all_backups[:-7]:
            os.remove(old)
            print(f"Removed old backup: {old}")

    print(f"Backup completed successfully: {dest_file} ({round(os.path.getsize(dest_file) / 1024, 2)} KB)")

if __name__ == "__main__":
    run_backup()
