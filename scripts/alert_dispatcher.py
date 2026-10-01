import json
import logging
import urllib.request
import urllib.error
from datetime import datetime

logger = logging.getLogger("AW1AlertDispatcher")
logging.basicConfig(level=logging.INFO)

WEBHOOK_URL = None  # Replace or export AW1_ALERT_WEBHOOK_URL in environment

def dispatch_statutory_breach_alert(
    event_type: str,
    society_code: str,
    reason: str,
    details: dict = None,
    webhook_url: str = None
) -> dict:
    """
    Dispatches a structured incident report for statutory non-compliance or circuit breaker halts.
    """
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Bilingual notification body
    alert_payload = {
        "event_type": event_type,
        "severity": "CRITICAL",
        "timestamp": timestamp,
        "society_code": society_code,
        "reason": reason,
        "details": details or {},
        "notices": {
            "en": f"[AW-1 BREACH HALT] Statutory compliance tripped for {society_code}: {reason}. Transaction intercepted.",
            "tn": f"[Tlhagiso ya Tshireletso] Tshegetso ya molao e emisitswe mo go {society_code}: {reason}. Phetisetso e thibilwe ka potlako."
        }
    }
    
    logger.warning("🚨 DISPATCHING COMPLIANCE HALT ALERT: %s", json.dumps(alert_payload, indent=2))
    
    target_url = webhook_url or WEBHOOK_URL
    if target_url:
        try:
            req = urllib.request.Request(
                target_url,
                data=json.dumps(alert_payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "AW1-Compliance-Alert/1.0"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                alert_payload["dispatch_status"] = f"HTTP {response.status}"
        except urllib.error.URLError as e:
            alert_payload["dispatch_status"] = f"FAILED: {str(e)}"
            logger.error("Failed to post alert to webhook: %s", e)
    else:
        alert_payload["dispatch_status"] = "LOGGED_LOCAL_NO_URL"

    return alert_payload

if __name__ == "__main__":
    test_res = dispatch_statutory_breach_alert(
        event_type="UNAUTHORIZED_DISBURSEMENT_HALT",
        society_code="LEO-RAN-01",
        reason="Citizen equity quota below statutory minimum 50.0%",
        details={"requested_pct": 32.5, "amount_bwp": 1500.0}
    )
    print("✓ Alert Dispatcher self-test completed:", test_res["dispatch_status"])
