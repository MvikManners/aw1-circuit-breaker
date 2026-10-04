"""
Laveto Wisdom AW-1 — Institutional Decision Gate SDK (Python 3.10+)
Zero-dependency client library for fintechs, commercial banks, and credit desks (CEDA/SEZA).
Handles rate-limiting with exponential backoff and HMAC-SHA256 webhook verification.
"""
import hmac
import time
import json
import hashlib
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

class LavetoWisdomError(Exception):
    pass

class CircuitBreakerHalt(LavetoWisdomError):
    def __init__(self, message: str, quotient: float, uncomfortable_truth: str):
        super().__init__(message)
        self.quotient = quotient
        self.uncomfortable_truth = uncomfortable_truth

class LavetoClient:
    def __init__(self, api_key: str, endpoint: str = "https://www.laveto.net/wisdom"):
        self.api_key = api_key
        self.base_url = endpoint.rstrip("/")

    def _post(self, path: str, payload: dict, max_retries: int = 3) -> dict:
        url = f"{self.base_url}{path}"
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "X-Laveto-Key": self.api_key,
            "User-Agent": "LavetoWisdom-SDK/1.0.0"
        }
        backoff = 1.0

        for attempt in range(max_retries):
            req = urllib.request.Request(url, data=data, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8")
                if e.code == 429 and attempt < max_retries - 1:
                    time.sleep(backoff)
                    backoff *= 2.0
                    continue
                try:
                    err_json = json.loads(body)
                    raise LavetoWisdomError(f"HTTP {e.code}: {err_json.get('message', body)}")
                except Exception:
                    raise LavetoWisdomError(f"HTTP {e.code}: {body}")
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(backoff)
                    backoff *= 2.0
                    continue
                raise LavetoWisdomError(f"Network error communicating with Laveto Wisdom: {e}")

    def audit_proposal(self, proposal: str, domain: str = "GENERAL", raise_on_halt: bool = False) -> dict:
        result = self._post("/api/v1/audit", {"proposal": proposal, "domain": domain})
        posture = result.get("final_posture", "PROCEED")
        quotient = result.get("wisdom_quotient", 0.0)
        truth = result.get("the_uncomfortable_truth", "")

        if raise_on_halt and posture == "HALT":
            raise CircuitBreakerHalt(
                f"Wisdom Engine halted execution (Quotient: {quotient})",
                quotient=quotient,
                uncomfortable_truth=truth
            )
        return result

    def settle_audit_fee(self, audit_id: str, tier: str = "SME_ASSURANCE", carrier: str = "ORANGE_MONEY", carrier_tx_id: Optional[str] = None) -> dict:
        payload = {
            "tier": tier,
            "carrier": carrier,
            "carrier_tx_id": carrier_tx_id or f"TX-{int(time.time())}"
        }
        return self._post(f"/audit/{audit_id}/settle", payload)

    @staticmethod
    def verify_webhook_signature(payload_bytes: bytes, signature_header: str, api_secret: str) -> bool:
        if not signature_header:
            return False
        expected_sig = hmac.new(api_secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_sig, signature_header)
