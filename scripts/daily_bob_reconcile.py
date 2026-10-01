#!/usr/bin/env python3
"""
scripts/daily_bob_reconcile.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Automated End-of-Day Settlement & Float Reconciliation for Bank of Botswana.
Executes daily at 23:55 CAT to certify 1-to-1 trust backing under the NCSS Act 2022.
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone
import urllib.request
import urllib.error

# Ensure aw1 modules can be resolved directly
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

LOG_PATH = os.path.join(BASE_DIR, 'compliance_audit.log')
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

API_ENDPOINT = "https://p20.laveto.net/wisdom/api/v1/compliance/trust-audit"


def fetch_daily_balances():
    """
    Retrieves end-of-day balances from core ledger/bank feeds.
    Replace or extend with live DB queries as needed.
    """
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Example daily balance extract (replace with dynamic query if integrated with SQL ledger)
    return {
        "audit_date": today_str,
        "custodian_bank": "First National Bank Botswana",
        "escrow_fiat_balance_bwp": 5250000.00,
        "circulating_float_bwp": 5000000.00,
        "pending_settlements_bwp": 200000.00
    }


def execute_reconciliation():
    payload_data = fetch_daily_balances()
    json_bytes = json.dumps(payload_data).encode('utf-8')
    
    req = urllib.request.Request(
        API_ENDPOINT,
        data=json_bytes,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            body = json.loads(resp.read().decode('utf-8'))
            
            seal = body.get("statutory_certificate", {}).get("statutory_seal_sha256")
            posture = body.get("runtime_posture")
            
            logging.info(
                f"RECONCILIATION SUCCESS | Date: {payload_data['audit_date']} | "
                f"Posture: {posture} | Seal: {seal} | Ratio: {body.get('backing_ratio')}"
            )
            print(f"✓ Settlement Verified ({posture}). SHA-256 Seal: {seal}")
            return True
            
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        logging.error(f"RECONCILIATION BREACH / HALT | Status: {e.code} | Response: {err_body}")
        print(f"❌ Statutory Alert: Reconciliation failed with code {e.code}: {err_body}")
        return False
    except Exception as e:
        logging.error(f"SYSTEM ERROR: {e}")
        print(f"❌ Error executing reconciliation: {e}")
        return False


if __name__ == "__main__":
    execute_reconciliation()
