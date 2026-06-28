#!/bin/bash
# Gospel OS Storage Maintenance Protocol
find /home/LavetoLab/ -name "__pycache__" -type d -exec rm -rf {} +
find /home/LavetoLab/core/logs/ -name "*.log" -exec truncate -s 0 {} \;
echo "Storage Sanitized: $(date)" >> /home/LavetoLab/cleanup.log

