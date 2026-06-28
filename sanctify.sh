#!/bin/bash
# Protocol: Reclaim Storage Space
# 1. Clear caches
find /home/LavetoLab/ -name "__pycache__" -type d -exec rm -rf {} +
# 2. Clear volatile logs (if these are the ones you usually clear)
truncate -s 0 /home/LavetoLab/core/logs/*.log
# 3. Clear any temp session folders
rm -rf /home/LavetoLab/tmp/*
echo "Storage Sanitization Complete: $(date)"
