#!/bin/bash
TS=$(date +%Y%m%d_%H%M%S)
mkdir -p /home/LavetoLab/backups
python3 -c "import sqlite3; conn = sqlite3.connect('/home/LavetoLab/lvt_database.db'); conn.execute(f\"VACUUM INTO '/home/LavetoLab/backups/lvt_db_${TS}.db'\"); conn.close()"
# Remove snapshots older than 14 days to preserve disk quota
find /home/LavetoLab/backups/ -name "lvt_db_*.db" -mtime +14 -delete
echo "[$(date)] Backup completed successfully." >> /home/LavetoLab/backups/backup.log
