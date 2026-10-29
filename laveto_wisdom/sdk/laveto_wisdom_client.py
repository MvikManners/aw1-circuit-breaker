"""
Laveto Wisdom AW — Enterprise Client SDK for Fintech & Credit Gates.
Drop-in client module providing resilient HTTP audit dispatching, automatic retry
with exponential backoff, quota inspection, and circuit-breaker posture evaluation.
"""
import time
import hmac
import hashlib
import requests
from typing import Dict, Any, Optional

DEFAULT_ENDPOINT = "https://p20.laveto.net/wisdom/api/v1/audit"

class LavetoWisdomError(Exception):
    """Base exception for Laveto Wisdom SDK errors."""
    pass

class CircuitBreakerHalt(LavetoWisdomError):
    """Raised when an audited proposal violates statutory or downside risk thresholds."""
    def __init__(self, audit_id: str, quotient: float, truth: str):
        super().__init__(f"Audit {audit_id} HALTED (Wisdom Quotient: {quotient}): {truth}")
        self.audit_id = audit_id
        self.quotient = quotient
        self.truth = truth

class QuotaExceededError(LavetoWisdomError):
    """Raised when monthly allocated audit limits are reached."""
    pass

class LavetoClient:
    def __init__(self, api_key: str, endpoint: str = DEFAULT_ENDPOINT, max_retries: int = 3):
        if not api_key:
            raise ValueError("An active 'api_key' is required to initialize LavetoClient.")
        self.api_key = api_key
        self.endpoint = endpoint
        self.max_retries = max_retries
        self.last_remaining_quota: Optional[int] = None

    def audit_proposal(self, proposal_text: str, raise_on_halt: bool = False) -> Dict[str, Any]:
        """
        Executes a 5-pass Decision Assurance audit against Botswana statutory baselines.
        
        :param proposal_text: The credit application, procurement decree, or investment plan.
        :param raise_on_halt: If True, raises CircuitBreakerHalt on HALT posture.
        :return: Full audited JSON dossier.
        """
        headers = {
            "Content-Type": "application/json",
            "X-Laveto-Key": self.api_key,
            "User-Agent": "Laveto-SDK-Python/1.0"
        }
        payload = {"proposal": proposal_text}

        delay = 1.0
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.post(self.endpoint, json=payload, headers=headers, timeout=30.0)

                # Track quota remaining header
                quota_header = response.headers.get("X-RateLimit-Remaining-Quota")
                if quota_header is not None:
                    self.last_remaining_quota = int(quota_header)

                if response.status_code == 200:
                    dossier = response.json()
                    posture = dossier.get("posture", "HALT")

                    if raise_on_halt and posture == "HALT":
                        truth = dossier.get("passes", {}).get("pass_5_verdict", {}).get("the_uncomfortable_truth", "")
                        quotient = float(dossier.get("wisdom_quotient", 0.0))
                        raise CircuitBreakerHalt(dossier.get("audit_id", "UNKNOWN"), quotient, truth)

                    return dossier

                elif response.status_code == 429:
                    retry_after = int(response.json().get("retry_after_seconds", 60))
                    time.sleep(retry_after)
                    continue

                elif response.status_code == 403:
                    raise QuotaExceededError("Monthly API audit quota exhausted for this key.")

                elif response.status_code >= 500:
                    if attempt == self.max_retries:
                        raise LavetoWisdomError(f"Server error HTTP {response.status_code}: {response.text}")
                    time.sleep(delay)
                    delay *= 2
                    continue

                else:
                    raise LavetoWisdomError(f"API request failed with HTTP {response.status_code}: {response.text}")

            except requests.RequestException as exc:
                if attempt == self.max_retries:
                    raise LavetoWisdomError(f"Network transport failure: {exc}") from exc
                time.sleep(delay)
                delay *= 2

        raise LavetoWisdomError("Max retries exceeded while executing audit.")

    @staticmethod
    def verify_webhook_signature(payload_bytes: bytes, signature_header: str, secret: str) -> bool:
        """Validates incoming HMAC-SHA256 webhook signatures from Laveto."""
        expected = hmac.new(secret.encode('utf-8'), payload_bytes, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature_header)
