import hashlib
import hmac
import json
import sqlite3
from datetime import datetime, timezone

DB_PATH = '/home/LavetoLab/lvt_database.db'

class QuorumVerificationError(Exception):
    pass

class QuorumEngine:
    """
    Cryptographic multi-agent quorum verification engine for high-impact tool execution.
    """
    
    CRITICAL_TOOLS = {
        'fund_transfer',
        'database_drop',
        'cloud_provision',
        'modify_iam_policy',
        'bulk_export_pii'
    }

    @staticmethod
    def get_agent_secret(agent_id: str):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        row = c.execute(
            "SELECT secret_key FROM agent_quorum_registry WHERE agent_id = ? AND status = 'ACTIVE'", 
            (agent_id,)
        ).fetchone()
        conn.close()
        return row[0] if row else None

    @classmethod
    def compute_signature(cls, agent_id: str, tool_name: str, payload_hash: str, nonce: str, timestamp: str) -> str:
        secret = cls.get_agent_secret(agent_id)
        if not secret:
            raise QuorumVerificationError(f"Agent '{agent_id}' not enrolled in active registry.")
        canonical = f"{agent_id}:{tool_name}:{payload_hash}:{nonce}:{timestamp}"
        return hmac.new(secret.encode('utf-8'), canonical.encode('utf-8'), hashlib.sha256).hexdigest()

    @classmethod
    def verify_attestations(cls, tool_name: str, payload: str, attestations: list, threshold: int = 2):
        """
        Validates m-of-n agent attestations against the canonical payload hash.
        attestations format:
        [
            {"agent_id": "agent_planner", "nonce": "abc1", "timestamp": "...", "signature": "..."},
            {"agent_id": "agent_auditor", "nonce": "abc2", "timestamp": "...", "signature": "..."}
        ]
        """
        payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        now = datetime.now(timezone.utc).isoformat()
        signers = []

        if not attestations or len(attestations) < threshold:
            reason = f"Threshold unmet: provided {len(attestations) if attestations else 0}, required {threshold}."
            cls._log_quorum_result(now, tool_name, payload_hash, threshold, [], "REJECTED", reason)
            return False, reason, None

        seen_agents = set()
        for att in attestations:
            aid = att.get("agent_id")
            nonce = att.get("nonce")
            ts = att.get("timestamp")
            sig = att.get("signature")

            if not all([aid, nonce, ts, sig]):
                reason = f"Malformed attestation packet from agent: {aid}"
                cls._log_quorum_result(now, tool_name, payload_hash, threshold, signers, "REJECTED", reason)
                return False, reason, None

            if aid in seen_agents:
                reason = f"Duplicate attestation detected: agent '{aid}' signed more than once."
                cls._log_quorum_result(now, tool_name, payload_hash, threshold, signers, "REJECTED", reason)
                return False, reason, None

            expected_sig = cls.compute_signature(aid, tool_name, payload_hash, nonce, ts)
            if not hmac.compare_digest(expected_sig, sig):
                reason = f"Cryptographic signature mismatch for agent '{aid}'."
                cls._log_quorum_result(now, tool_name, payload_hash, threshold, signers, "REJECTED", reason)
                return False, reason, None

            seen_agents.add(aid)
            signers.append(aid)

        if len(signers) >= threshold:
            quorum_id = hashlib.sha256(f"{payload_hash}:{','.join(sorted(signers))}:{now}".encode('utf-8')).hexdigest()
            cls._log_quorum_result(now, tool_name, payload_hash, threshold, signers, "APPROVED", None, quorum_id)
            return True, "QUORUM_VERIFIED", quorum_id
        else:
            reason = f"Insufficient valid signers: {len(signers)}/{threshold}"
            cls._log_quorum_result(now, tool_name, payload_hash, threshold, signers, "REJECTED", reason)
            return False, reason, None

    @staticmethod
    def _log_quorum_result(timestamp, tool_name, payload_hash, threshold, signers, status, reason=None, quorum_id=None):
        if not quorum_id:
            quorum_id = hashlib.sha256(f"{payload_hash}:{timestamp}".encode('utf-8')).hexdigest()
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""
                INSERT INTO quorum_audit_ledger 
                (quorum_id, timestamp, tool_name, payload_hash, threshold_required, signers, status, rejection_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (quorum_id, timestamp, tool_name, payload_hash, threshold, json.dumps(signers), status, reason))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[QUORUM LEDGER ERROR]: {e}")
