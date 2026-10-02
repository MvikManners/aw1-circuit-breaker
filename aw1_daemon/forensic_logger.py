"""
aw1_daemon/forensic_logger.py
Cryptographic audit logger connecting daemon containment events to SQLite.
"""
import sqlite3
import hashlib
import json
import time
import os
from typing import Dict, Any

DB_PATH = "/home/LavetoLab/lvt_backend/lvt_database.db"

class ForensicLogger:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_table()

    def _init_table(self):
        try:
            if not os.path.exists(os.path.dirname(self.db_path)):
                return
            with sqlite3.connect(self.db_path, timeout=10.0) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS daemon_security_incidents (
                        incident_id TEXT PRIMARY KEY,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        actor_id TEXT,
                        posture TEXT,
                        gate TEXT,
                        reason TEXT,
                        command_digest TEXT,
                        payload TEXT
                    )
                """)
                conn.commit()
        except Exception:
            pass

    def log_incident(self, actor_id: str, command: str, gate: str, reason: str) -> str:
        incident_id = f"INC-{hashlib.sha256(f'{time.time()}:{command}'.encode()).hexdigest()[:10].upper()}"
        cmd_digest = hashlib.sha256(command.encode()).hexdigest()
        
        try:
            with sqlite3.connect(self.db_path, timeout=10.0) as conn:
                conn.execute("""
                    INSERT INTO daemon_security_incidents
                    (incident_id, actor_id, posture, gate, reason, command_digest, payload)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (incident_id, actor_id, "HALT", gate, reason, cmd_digest, command[:500]))
                conn.commit()
        except Exception:
            pass

        return incident_id
