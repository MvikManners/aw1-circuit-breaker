"""
aw1.reversibility
~~~~~~~~~~~~~~~~~
Two-Way vs. One-Way Door Causal Execution Interlock.
Routes reversible actions to Tier 1 (<0.02ms Fast-Path) and irreversible
actions to Tier 2 (Gate 7 Quorum / Cryptographic Hold).
"""

from enum import Enum
from typing import Dict, Any, Optional, Set
import re
import hmac
import hashlib
import time


class DoorType(str, Enum):
    TWO_WAY = "TWO_WAY_DOOR"    # Reversible: Low risk, instant bypass
    ONE_WAY = "ONE_WAY_DOOR"    # Irreversible: High consequence, holds for validation


class ReversibilityDecision:
    def __init__(
        self,
        door_type: DoorType,
        tier: int,
        approved: bool,
        reason: str,
        execution_grant: Optional[str] = None
    ):
        self.door_type = door_type
        self.tier = tier
        self.approved = approved
        self.reason = reason
        self.execution_grant = execution_grant

    def to_dict(self) -> Dict[str, Any]:
        return {
            "door_type": self.door_type.value,
            "tier": self.tier,
            "approved": self.approved,
            "reason": self.reason,
            "execution_grant": self.execution_grant
        }


class ReversibilityRouter:
    """
    Two-Tier Causal Router separating routine reads from irreversible mutations.
    """
    
    ONE_WAY_PATTERNS: Set[str] = {
        r"payout", r"transfer", r"disburse", r"liquidate", r"settle",
        r"drop\s+table", r"truncate", r"delete\s+from", r"rm\s+-rf",
        r"chmod", r"chown", r"iptables", r"curl\s+.*\|\s*sh", r"docker\s+run"
    }

    TWO_WAY_PATTERNS: Set[str] = {
        r"select\s+.*\s+from", r"read", r"lookup", r"get_", r"fetch",
        r"status", r"inspect", r"verify", r"audit_check"
    }

    def __init__(self, hmac_secret: str = "aw1-causal-secret-entropy"):
        self.secret = hmac_secret.encode("utf-8")

    def classify_action(self, action_signature: str, payload: str = "") -> DoorType:
        combined = f"{action_signature} {payload}".lower()

        for pattern in self.ONE_WAY_PATTERNS:
            if re.search(pattern, combined):
                return DoorType.ONE_WAY

        for pattern in self.TWO_WAY_PATTERNS:
            if re.search(pattern, combined):
                return DoorType.TWO_WAY

        if any(verb in combined for verb in ["write", "update", "push", "send", "post"]):
            return DoorType.ONE_WAY

        return DoorType.TWO_WAY

    def evaluate(self, actor: str, action_signature: str, payload: str = "") -> ReversibilityDecision:
        door = self.classify_action(action_signature, payload)

        if door == DoorType.TWO_WAY:
            token = self._mint_grant(actor, action_signature, "TIER1_REVERSIBLE")
            return ReversibilityDecision(
                door_type=DoorType.TWO_WAY,
                tier=1,
                approved=True,
                reason="Tier 1 Pre-Check Cleared: Reversible Two-Way Door action.",
                execution_grant=token
            )

        return ReversibilityDecision(
            door_type=DoorType.ONE_WAY,
            tier=2,
            approved=False,
            reason="Gate 7 Interlock Tripped: Irreversible One-Way Door detected. Awaiting Tier 2 cryptographic clearance.",
            execution_grant=None
        )

    def _mint_grant(self, actor: str, action: str, tier_tag: str) -> str:
        timestamp = str(int(time.time()))
        msg = f"{actor}:{action}:{tier_tag}:{timestamp}".encode("utf-8")
        sig = hmac.new(self.secret, msg, hashlib.sha256).hexdigest()[:16]
        return f"AW1-GRANT-{tier_tag}-{timestamp}-{sig}"
