"""
Laveto Wisdom AW — Asynchronous Webhook Event Dispatcher with Telemetry Logging & HMAC-SHA256 Signing.
Fires cryptographically signed alert payloads to registered client webhooks when critical HALT postures trigger.
"""
import time
import json
import hmac
import hashlib
import sqlite3
import threading
import requests
from datetime import datetime

DB_PATH = "/home/LavetoLab/lvt_backend/lvt_database.db"

def _sign_payload(payload_bytes: bytes, secret_key: str) -> str:
    """Generates an HMAC-SHA256 hex digest for request integrity validation."""
    return hmac.new(secret_key.encode('utf-8'), payload_bytes, hashlib.sha256).hexdigest()

def _dispatch_worker(webhook_url: str, client_id: str, client_secret: str, audit_data: dict):
    start_time = time.time()
    audit_id = audit_data.get("audit_id", "UNKNOWN")
    posture = audit_data.get("posture", "HALT")
    
    payload_dict = {
        "event": "audit.circuit_breaker_halt",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "client_id": client_id,
        "audit_id": audit_id,
        "posture": posture,
        "wisdom_quotient": audit_data.get("wisdom_quotient"),
        "the_uncomfortable_truth": audit_data.get("passes", {}).get("pass_5_verdict", {}).get("the_uncomfortable_truth", ""),
        "dossier_url": f"https://p20.laveto.net/wisdom/audit/{audit_id}"
    }
    
    payload_bytes = json.dumps(payload_dict, sort_keys=True).encode('utf-8')
    signature = _sign_payload(payload_bytes, client_secret) if client_secret else ""
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Laveto-Wisdom-AW-CircuitBreaker/1.0",
        "X-Laveto-Signature": signature,
        "X-Laveto-Timestamp": str(int(start_time))
    }

    http_status = None
    err_msg = None

    try:
        resp = requests.post(webhook_url, data=payload_bytes, headers=headers, timeout=6.0)
        http_status = resp.status_code
        latency_ms = round((time.time() - start_time) * 1000, 2)
        print(f"[Webhook] Delivered to {client_id} ({webhook_url}) - HTTP {http_status} ({latency_ms}ms)")
    except Exception as err:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        err_msg = str(err)
        print(f"[Webhook Error] Failed dispatch to {webhook_url} for {client_id}: {err_msg}")

    # Persist delivery telemetry
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        with conn:
            conn.execute("""
                INSERT INTO wisdom_webhook_logs 
                (client_id, audit_id, webhook_url, posture, http_status, delivery_latency_ms, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (client_id, audit_id, webhook_url, posture, http_status, latency_ms, err_msg))
        conn.close()
    except Exception as db_err:
        print(f"[Webhook DB Error] Could not persist log: {db_err}")

def trigger_circuit_breaker_webhook(client_id: str, audit_data: dict):
    """Spawns non-blocking thread to dispatch cryptographically signed webhook if configured for client."""
    if audit_data.get("posture") != "HALT":
        return

    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT webhook_url, api_key FROM wisdom_api_clients WHERE client_id = ?", (client_id,)).fetchone()
        conn.close()

        if row and row["webhook_url"]:
            t = threading.Thread(
                target=_dispatch_worker,
                args=(row["webhook_url"], client_id, row["api_key"], audit_data),
                daemon=True
            )
            t.start()
    except Exception as e:
        print(f"[Webhook Error] Lookup failed: {e}")
