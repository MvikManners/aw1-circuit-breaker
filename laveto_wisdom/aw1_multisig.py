import hmac
import hashlib
import json
import time

# Enterprise Council Keystore (M-of-N Fiduciary Signers)
COUNCIL_KEYS = {
    "fiduciary-officer-01": "aw1_sec_fid01_77a9c3d4e8b10f22",
    "risk-director-02":     "aw1_sec_risk02_44f8e2a1b9c03d77",
    "general-counsel-03":   "aw1_sec_gc03_99e1a8b4c2d30f66"
}

QUORUM_THRESHOLD = 2  # 2-of-3 approval required

def compute_proposal_hash(actor_id: str, tool_name: str, payload: str, timestamp: int) -> str:
    """Canonical SHA-256 digest of the one-way door operation proposal."""
    payload_clean = payload.strip()
    raw = f"{actor_id}:{tool_name}:{payload_clean}:{timestamp}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def verify_multisig_approval(approval_data: dict, actor_id: str, tool_name: str, payload: str) -> tuple[bool, str, list]:
    """
    Validates cryptographic M-of-N multi-sig quorum.
    Returns: (is_valid: bool, reason: str, verified_approvers: list)
    """
    if not isinstance(approval_data, dict):
        return False, "Invalid multi-sig payload structure", []

    proposal_ts = approval_data.get("timestamp")
    signatures = approval_data.get("signatures", {})  # {signer_id: signature_hex}

    if not proposal_ts or not isinstance(signatures, dict):
        return False, "Malformed approval structure: missing timestamp or signatures dict", []

    # Enforce multi-sig challenge TTL (5 minutes)
    now = int(time.time())
    if abs(now - int(proposal_ts)) > 300:
        return False, f"Multi-sig approval expired (age: {now - int(proposal_ts)}s, limit: 300s)", []

    proposal_hash = compute_proposal_hash(actor_id, tool_name, payload, int(proposal_ts))

    verified_approvers = []
    for signer_id, sig in signatures.items():
        secret = COUNCIL_KEYS.get(signer_id)
        if not secret:
            continue

        expected_sig = hmac.new(
            secret.encode("utf-8"),
            proposal_hash.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        if hmac.compare_digest(sig, expected_sig):
            verified_approvers.append(signer_id)

    if len(verified_approvers) >= QUORUM_THRESHOLD:
        return True, f"Quorum met ({len(verified_approvers)}/{QUORUM_THRESHOLD} signatures verified)", verified_approvers

    return False, f"Quorum failure: only {len(verified_approvers)}/{QUORUM_THRESHOLD} verified signatures", verified_approvers
