#!/bin/bash
set -euo pipefail

LOG_DIR="/home/LavetoLab"
BACKUP_DIR="/home/LavetoLab/backups"

echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] Starting Routine Log & Snapshot Pruning ==="

# 1. Truncate logs larger than 5 MB
for logfile in "${LOG_DIR}/cleanup.log" "${LOG_DIR}/tokenomics_debug.log" "${BACKUP_DIR}/backup_cron.log"; do
    if [ -f "$logfile" ] && [ $(stat -c%s "$logfile") -gt 5242880 ]; then
        tail -n 2000 "$logfile" > "${logfile}.tmp" && mv "${logfile}.tmp" "$logfile"
        echo "Truncated large log: $logfile"
    fi
done

# 2. Retain SQLite database snapshots from the last 14 days; prune older files
if [ -d "$BACKUP_DIR" ]; then
    DELETED_COUNT=$(find "$BACKUP_DIR" -name "*.db" -type f -mtime +14 -delete -print | wc -l)
    echo "Pruned $DELETED_COUNT database snapshot(s) older than 14 days."
fi

echo "=== Maintenance Completed Successfully ==="
