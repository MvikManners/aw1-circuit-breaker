import os
import json
import time
import hmac
import hashlib
import secrets
import re
from datetime import datetime, timezone
from flask import request, jsonify

AW1_HMAC_SECRET = os.environ.get("AW1_HMAC_SECRET", "aw1-sovereign-enterprise-secret-key-2026").encode("utf-8")

def append_telemetry(event_dict):
    try:
        from laveto_wisdom.aw1_storage import AW1StorageEngine
        AW1StorageEngine.append_telemetry(event_dict)
    except Exception:
        pass

def handle_intercept():
    if request.method == "OPTIONS":
        resp = jsonify({"status": "ok"})
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return resp, 200

    start_time = time.perf_counter()

    # --- PHASE 1: STRICT RFC-8259 INGRESS PARSER ---
    raw_data = request.get_data()
    if not raw_data:
        lat = round((time.perf_counter() - start_time) * 1000, 3)
        return jsonify({
            "status": "HALT_AND_CONTAIN",
            "verdict": "FAIL_CLOSED",
            "permitted": False,
            "actor_id": "malformed_request",
            "tool_name": "unknown",
            "token": None,
            "reason": "RFC-8259 Ingress Violation: Empty request body",
            "latency_ms": lat,
            "circuit_breaker": "AW-1 Sovereign Execution Arbitrator"
        }), 400

    try:
        data = json.loads(raw_data.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Root payload must be an Object")
    except Exception as parse_err:
        lat = round((time.perf_counter() - start_time) * 1000, 3)
        return jsonify({
            "status": "HALT_AND_CONTAIN",
            "verdict": "FAIL_CLOSED",
            "permitted": False,
            "actor_id": "malformed_request",
            "tool_name": "unknown",
            "token": None,
            "reason": f"RFC-8259 Ingress Rejection: Malformed JSON syntax ({str(parse_err)})",
            "latency_ms": lat,
            "circuit_breaker": "AW-1 Sovereign Execution Arbitrator"
        }), 400

    actor_id = data.get("actor_id")
    tool_name = data.get("tool_name")
    payload = data.get("payload")

    if not actor_id or not tool_name or payload is None:
        lat = round((time.perf_counter() - start_time) * 1000, 3)
        return jsonify({
            "status": "HALT_AND_CONTAIN",
            "verdict": "FAIL_CLOSED",
            "permitted": False,
            "actor_id": str(actor_id or "missing"),
            "tool_name": str(tool_name or "missing"),
            "token": None,
            "reason": "Schema Validation Rejection: Missing required fields (actor_id, tool_name, payload)",
            "latency_ms": lat,
            "circuit_breaker": "AW-1 Sovereign Execution Arbitrator"
        }), 400

    actor_id = str(actor_id).strip()
    tool_name = str(tool_name).strip()
    payload = str(payload)

    # --- PHASE 5: CRYPTOGRAPHIC AGENT IDENTITY VERIFICATION ---
    from laveto_wisdom.aw1_identity import verify_agent_request
    is_auth, verified_actor, auth_reason = verify_agent_request(request.headers, actor_id, tool_name, payload)
    if not is_auth:
        lat = round((time.perf_counter() - start_time) * 1000, 3)
        return jsonify({
            "status": "HALT_AND_CONTAIN",
            "verdict": "FAIL_CLOSED",
            "permitted": False,
            "actor_id": verified_actor,
            "tool_name": tool_name,
            "token": None,
            "reason": f"Gate 0 Cryptographic Authentication Rejection: {auth_reason}",
            "latency_ms": lat,
            "circuit_breaker": "AW-1 Sovereign Execution Arbitrator"
        }), 401

    # 1. Readonly SQL Policy Enforcement
    mutation_pattern = r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE|GRANT|REVOKE)\b"
    is_mutation = bool(re.search(mutation_pattern, payload, re.IGNORECASE)) and any(kw in tool_name.lower() for kw in ["sql", "db", "query"])

    # 2. Known Privileged Shell / Egress Primitives
    dangerous_patterns = [
        r"\b(subprocess|os\.system|os\.popen|pty\.spawn|shutil\.rmtree)\b",
        r"\b(socket\.socket|requests\.post|urllib\.request)\b",
        r"\b(rm\s+-rf|mkfs|chmod\s+777|chown|dd\s+if=)\b",
        r"\b(eval\(|exec\(|__import__)\b",
        r"/etc/(passwd|shadow)",
        r"nc\s+[\d\.]+\s+\d+",
        r"(__class__|__bases__|__subclasses__|__globals__|__builtins__|__code__)",
        r"(base64\s+(-d|--decode)|\|\s*(bash|sh|python\d*))"
    ]
    is_exploit = any(re.search(pat, payload, re.IGNORECASE) for pat in dangerous_patterns)

    # 3. Static AST Breaker Verification
    breaker_status = "PERMITTED"
    breaker_reason = "Payload verified safe by AST policy"
    try:
        import sys
        if "/home/LavetoLab/aw1-breaker" not in sys.path:
            sys.path.insert(0, "/home/LavetoLab/aw1-breaker")
        from aw1.breaker import ASTCircuitBreaker
        breaker = ASTCircuitBreaker()
        v_obj = breaker.intercept(actor_id=actor_id, tool_name=tool_name, payload=payload)
        v_status = getattr(v_obj, "status", None) or getattr(v_obj, "verdict", None)
        if v_status in ("HALT_AND_CONTAIN", "FAIL_CLOSED", "CONTAINED", "TRIPPED"):
            breaker_status = "HALT_AND_CONTAIN"
            breaker_reason = getattr(v_obj, "containment_reason", None) or getattr(v_obj, "reason", None) or "AST Circuit Breaker containment triggered"
    except Exception as e:
        breaker_status = "HALT_AND_CONTAIN"
        breaker_reason = f"AST Engine Containment Alert: {str(e)}"

        # --- PHASE 6: ONE-WAY DOOR MULTI-SIG COUNCIL INTERLOCK ---
    is_one_way_door = "HIGH_VALUE_ONE_WAY_DOOR" in str(breaker_reason)
    multisig_approved = False
    approvers = []

    if is_one_way_door:
        approval_header = request.headers.get("X-AW1-MultiSig-Approval")
        if approval_header:
            try:
                from laveto_wisdom.aw1_multisig import verify_multisig_approval
                approval_payload = json.loads(approval_header)
                multisig_approved, ms_reason, approvers = verify_multisig_approval(
                    approval_payload, actor_id, tool_name, payload
                )
                if multisig_approved:
                    breaker_status = "PERMITTED"
                    breaker_reason = f"Execution elevated via Multi-Sig Quorum: {', '.join(approvers)}"
            except Exception as e:
                multisig_approved = False

    if is_mutation:
        status = "HALT_AND_CONTAIN"
        permitted = False
        reason = "Database mutation rejected under readonly_sql enterprise policy"
        token = None
    elif is_exploit or breaker_status == "HALT_AND_CONTAIN":
        status = "HALT_AND_CONTAIN"
        permitted = False
        reason = breaker_reason if breaker_status == "HALT_AND_CONTAIN" else "Malicious execution primitive detected"
        token = None
    else:
        status = "PERMITTED"
        permitted = True
        reason = "Policy evaluation completed: execution safe"

        # --- PHASE 2: EPHEMERAL HMAC-SHA256 TOKEN MINTING ---
        nonce = secrets.token_hex(8)
        now_ts = int(time.time())
        expires_at = now_ts + 5
        payload_digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
        sig_base = f"{nonce}:{actor_id}:{tool_name}:{payload_digest}:{expires_at}".encode("utf-8")
        sig = hmac.new(AW1_HMAC_SECRET, sig_base, hashlib.sha256).hexdigest()[:16]
        token = f"aw1_v1.{nonce}.{expires_at}.{sig}"

    latency_ms = round((time.perf_counter() - start_time) * 1000, 3)

    # --- PHASE 4: ATOMIC TELEMETRY PERSISTENCE ---
    append_telemetry({
        "id": f"EVT-{int(time.time()*1000)%100000}",
        "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
        "actor": actor_id,
        "tool": tool_name,
        "permitted": permitted,
        "status": status,
        "latency_ms": latency_ms,
        "reason": reason
    })

    resp = jsonify({
        "status": status,
        "verdict": "PASS" if permitted else "FAIL_CLOSED",
        "permitted": permitted,
        "actor_id": actor_id,
        "tool_name": tool_name,
        "token": token,
        "reason": reason,
        "latency_ms": latency_ms,
        "circuit_breaker": "AW-1 Sovereign Execution Arbitrator"
    })
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp, 200

def handle_token_burn():
    if request.method == "OPTIONS":
        resp = jsonify({"status": "ok"})
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return resp, 200

    raw = request.get_data()
    try:
        data = json.loads(raw.decode("utf-8")) if raw else {}
    except Exception:
        return jsonify({"valid": False, "reason": "Malformed JSON"}), 400

    token = str(data.get("token", "")).strip()
    actor_id = str(data.get("actor_id", "")).strip()
    tool_name = str(data.get("tool_name", "")).strip()
    payload = str(data.get("payload", ""))

    parts = token.split(".")
    if len(parts) != 4 or parts[0] != "aw1_v1":
        return jsonify({"valid": False, "reason": "Invalid token format or version"}), 403

    _, nonce, expires_at_str, signature = parts
    try:
        expires_at = int(expires_at_str)
    except ValueError:
        return jsonify({"valid": False, "reason": "Invalid expiration timestamp"}), 403

    now_ts = int(time.time())
    if now_ts > expires_at:
        return jsonify({
            "valid": False,
            "status": "REVOKED",
            "reason": f"Execution Token Expired (TTL 5s exceeded by {now_ts - expires_at}s)"
        }), 403

    payload_digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    expected_base = f"{nonce}:{actor_id}:{tool_name}:{payload_digest}:{expires_at}".encode("utf-8")
    expected_sig = hmac.new(AW1_HMAC_SECRET, expected_base, hashlib.sha256).hexdigest()[:16]

    if not hmac.compare_digest(signature, expected_sig):
        return jsonify({
            "valid": False,
            "status": "CONTAINED",
            "reason": "Cryptographic Signature Mismatch (Token forgery or tampering detected)"
        }), 403

    # --- PHASE 4: ATOMIC NONCE BURNING WITH POSIX LOCKING ---
    from laveto_wisdom.aw1_storage import AW1StorageEngine
    if not AW1StorageEngine.burn_nonce_atomic(nonce):
        return jsonify({
            "valid": False,
            "status": "CONTAINED",
            "reason": "Replay Attack Neutralized: Token nonce has already been burned"
        }), 409

    return jsonify({
        "valid": True,
        "status": "TOKEN_BURNED_EXECUTION_AUTHORIZED",
        "actor_id": actor_id,
        "tool_name": tool_name,
        "nonce": nonce
    }), 200
