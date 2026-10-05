import os
import hmac
import hashlib
import json
import sqlite3
import logging
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify

lemon_webhook_bp = Blueprint('lemon_webhook', __name__)

DB_PATH = "/home/LavetoLab/lvt_database.db"
LOG_PATH = "/home/LavetoLab/tokenomics_debug.log"

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] LEMON_WEBHOOK: %(message)s'
)

def init_lemon_tables():
    """Ensure persistence tables exist for Lemon Squeezy orders and subscriptions."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lemon_webhook_events (
                event_id TEXT PRIMARY KEY,
                event_name TEXT NOT NULL,
                order_id TEXT,
                customer_email TEXT,
                amount_cents INTEGER,
                currency TEXT,
                status TEXT,
                raw_payload TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS active_license_keys (
                license_key TEXT PRIMARY KEY,
                order_id TEXT,
                customer_email TEXT,
                plan_tier TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Failed to initialize lemon tables: {e}")

init_lemon_tables()

@lemon_webhook_bp.route('/webhook/lemonsqueezy', methods=['GET', 'POST'])
def lemon_callback():
    if request.method == 'GET':
        return jsonify({
            "status": "online",
            "endpoint": "/wisdom/webhook/lemonsqueezy",
            "note": "Ready to receive Lemon Squeezy POST webhook events"
        }), 200
    secret = os.environ.get("LEMONSQUEEZY_WEBHOOK_SECRET", "")
    signature = request.headers.get("X-Signature")

    # 1. Enforce signature validation if secret is set
    if secret:
        if not signature:
            logging.warning("Rejected webhook: Missing X-Signature header.")
            return jsonify({"error": "Missing signature header"}), 401
        
        computed_sig = hmac.new(
            secret.encode("utf-8"),
            request.get_data(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(computed_sig, signature):
            logging.warning("Rejected webhook: Invalid HMAC signature.")
            return jsonify({"error": "Invalid signature"}), 401

    raw_payload = request.get_data(as_text=True)
    try:
        payload = json.loads(raw_payload)
    except Exception as e:
        logging.error(f"Failed to parse JSON payload: {e}")
        return jsonify({"error": "Invalid JSON"}), 400

    meta = payload.get("meta", {})
    event_name = meta.get("event_name", "unknown")
    custom_data = meta.get("custom_data", {})
    data = payload.get("data", {})
    event_id = str(data.get("id", f"evt_{datetime.now(timezone.utc).timestamp()}"))
    attributes = data.get("attributes", {})

    order_id = str(attributes.get("order_number") or data.get("id") or "")
    customer_email = attributes.get("user_email") or attributes.get("customer_email") or ""
    amount_cents = attributes.get("total") or attributes.get("subtotal") or 0
    currency = attributes.get("currency", "USD")
    order_status = attributes.get("status", "unknown")

    logging.info(f"Received event '{event_name}' (ID: {event_id}) for {customer_email} - Status: {order_status}")

    # 2. Idempotency Check & Ledger Persistence
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        cursor = conn.cursor()

        # Check if already processed
        cursor.execute("SELECT event_id FROM lemon_webhook_events WHERE event_id = ?", (event_id,))
        if cursor.fetchone():
            conn.close()
            logging.info(f"Duplicate event '{event_id}' skipped.")
            return jsonify({"status": "duplicate_skipped"}), 200

        # Record raw event
        cursor.execute("""
            INSERT INTO lemon_webhook_events (
                event_id, event_name, order_id, customer_email,
                amount_cents, currency, status, raw_payload
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id, event_name, order_id, customer_email,
            amount_cents, currency, order_status, raw_payload
        ))

        # 3. Handle Order & License Activation Events
        if event_name in ["order_created", "subscription_created"]:
            plan_name = attributes.get("first_order_item", {}).get("product_name") or "Developer Pro"
            license_key = attributes.get("first_order_item", {}).get("license_key") or f"AW1-{os.urandom(8).hex().upper()}"

            cursor.execute("""
                INSERT OR REPLACE INTO active_license_keys (
                    license_key, order_id, customer_email, plan_tier, status
                ) VALUES (?, ?, ?, ?, ?)
            """, (license_key, order_id, customer_email, plan_name, "ACTIVE"))

            logging.info(f"Provisioned license key '{license_key}' for {customer_email} ({plan_name})")

        conn.commit()
        conn.close()

    except Exception as e:
        logging.error(f"Database error processing webhook: {e}")
        return jsonify({"error": "Database error", "details": str(e)}), 500

    return jsonify({
        "status": "processed",
        "event_name": event_name,
        "event_id": event_id
    }), 200
