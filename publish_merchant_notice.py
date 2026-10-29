#!/usr/bin/env python3
"""
Laveto Pay Bilingual Merchant Notice Dispatcher.
Deploys Reference LVT-OPS-2026-BOB-01 to Portal Banner and Email Broadcast Outbox.
"""

import sys
import os
import json
from datetime import datetime, timezone

sys.path.insert(0, "/home/LavetoLab")

from core import create_app, db
from core.models import Merchant

NOTICE_REF = "LVT-OPS-2026-BOB-01"
PUBLISH_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

NOTICE_PAYLOAD = {
    "reference": NOTICE_REF,
    "effective_date": "2026-10-18",
    "published_at": PUBLISH_DATE,
    "priority": "HIGH",
    "category": "STATUTORY_COMPLIANCE",
    "jurisdiction": "Bank of Botswana (NPS Act 2022 / NCSS Act)",
    "title_en": "Scheduled Nightly 1-to-1 Trust Account Reconciliation & Payout Window",
    "title_tn": "Tetlanyo ya Madi a Bagwebi Bosigo le Thulaganyo ya Pusetso-Madi",
    "summary_en": "Nightly automated trust reconciliation runs at 23:59 CAT with next-morning payouts between 06:00 and 09:00 CAT. 100% full-reserve backing verified.",
    "summary_tn": "Tetlanyo ya madi a bagwebi e diragala bosigo ka 23:59 CAT, dituelo di goroga magareng ga 06:00 le 09:00 mo mosong. Madi a sireletsegile ka botlalo (100%).",
    "details": {
        "audit_window": "Daily at 23:59 CAT (21:59 UTC)",
        "disbursement_window": "06:00 CAT – 09:00 CAT (EFT, Orange Money, Smega, MyZaka)",
        "backing_standard": "Bank of Botswana 1-to-1 Trust Parity (100.00%)",
        "custodian_banks": ["First National Bank Botswana (FNBB)", "Absa Bank Botswana"]
    }
}

def publish_portal_banner():
    """Writes persistent banner JSON for template rendering on the merchant portal dashboard."""
    banner_dir = "/home/LavetoLab/core/static/notices"
    os.makedirs(banner_dir, exist_ok=True)
    banner_file = os.path.join(banner_dir, "active_broadcast.json")
    
    with open(banner_file, "w", encoding="utf-8") as f:
        json.dump(NOTICE_PAYLOAD, f, indent=2)
    
    print(f"✅ Merchant portal banner fixture updated: {banner_file}")

def queue_email_broadcast():
    """Generates email broadcast queue entries for all registered merchants."""
    app = create_app()
    with app.app_context():
        merchants = Merchant.query.all()
        queue_sink = "/home/LavetoLab/mail_broadcast_queue.jsonl"
        
        queued_count = 0
        with open(queue_sink, "a", encoding="utf-8") as out:
            for m in merchants:
                recipient_email = getattr(m, "email", None) or getattr(m, "contact_email", None) or f"merchant_{m.id}@laveto.net"
                business_name = getattr(m, "business_name", None) or getattr(m, "name", f"Merchant #{m.id}")
                
                queue_item = {
                    "reference": NOTICE_REF,
                    "merchant_id": m.id,
                    "business_name": business_name,
                    "recipient_email": recipient_email,
                    "subject": f"[{NOTICE_REF}] Statutory Trust Reconciliation & Settlement Notice / Kitsiso ya Dituelo",
                    "queued_at": PUBLISH_DATE,
                    "status": "QUEUED"
                }
                out.write(json.dumps(queue_item) + "\n")
                queued_count += 1
                
        print(f"✅ Successfully queued {queued_count} merchant broadcast emails in {queue_sink}")

if __name__ == "__main__":
    print(f"🚀 Publishing Notice {NOTICE_REF}...")
    publish_portal_banner()
    queue_email_broadcast()
    print("🏁 Publication cycle completed successfully.")
