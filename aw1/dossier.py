"""
aw1.dossier
~~~~~~~~~~~
Tamper-Evident SHA-256 Decision Assurance Dossier Generator.
Produces cryptographically verifiable audit records for enterprise CROs and regulators.
"""

from typing import Dict, Any, List, Optional
import hashlib
import json
import time


class DecisionAssuranceDossier:
    def __init__(
        self,
        actor_id: str,
        action_signature: str,
        door_type: str,
        posture: str,  # HALT | CALIBRATE | PROCEED
        wisdom_quotient: float,
        blindspots: List[str],
        causal_order_impacts: Dict[str, str],
        parent_hash: str = "GENESIS_ROOT_0000000000000000"
    ):
        self.timestamp = int(time.time())
        self.actor_id = actor_id
        self.action_signature = action_signature
        self.door_type = door_type
        self.posture = posture
        self.wisdom_quotient = round(wisdom_quotient, 4)
        self.blindspots = blindspots
        self.causal_order_impacts = causal_order_impacts
        self.parent_hash = parent_hash
        self.dossier_hash = self._generate_sha256()

    def _payload_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "actor_id": self.actor_id,
            "action_signature": self.action_signature,
            "door_type": self.door_type,
            "posture": self.posture,
            "wisdom_quotient": self.wisdom_quotient,
            "blindspots": self.blindspots,
            "causal_order_impacts": self.causal_order_impacts,
            "parent_hash": self.parent_hash
        }

    def _generate_sha256(self) -> str:
        serialized = json.dumps(self._payload_dict(), sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def verify_integrity(self) -> bool:
        """Verifies whether the payload matches its cryptographic digest."""
        return self._generate_sha256() == self.dossier_hash

    def to_dict(self) -> Dict[str, Any]:
        data = self._payload_dict()
        data["dossier_hash"] = self.dossier_hash
        return data


class AssuranceEngine:
    @staticmethod
    def generate_halt_dossier(
        actor_id: str,
        action: str,
        reason: str,
        parent_hash: str = "GENESIS_ROOT_0000000000000000"
    ) -> DecisionAssuranceDossier:
        return DecisionAssuranceDossier(
            actor_id=actor_id,
            action_signature=action,
            door_type="ONE_WAY_DOOR",
            posture="HALT",
            wisdom_quotient=0.0100,
            blindspots=[reason, "Irreversible state mutation without multi-party quorum."],
            causal_order_impacts={
                "1st_order": "Immediate tool execution blocked at execution gate.",
                "2nd_order": "Actor token revoked; process quarantined.",
                "3rd_order": "Infrastructure state preserved from catastrophic failure/unauthorized liquidity drainage."
            },
            parent_hash=parent_hash
        )
