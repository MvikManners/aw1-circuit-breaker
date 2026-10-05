#!/bin/bash
set -e

BACKUP_DIR="/home/LavetoLab/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

find /home/LavetoLab -maxdepth 3 -name "*.db" -not -path "*/backups/*" | while read -r DB_FILE; do
    DB_NAME=$(basename "$DB_FILE" .db)
    TARGET="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.db"
    sqlite3 "$DB_FILE" ".backup '$TARGET'"
    echo "Backed up $DB_FILE -> $TARGET"
done

# Keep only the last 14 days of backups
find "$BACKUP_DIR" -name "*.db" -type f -mtime +14 -delete
