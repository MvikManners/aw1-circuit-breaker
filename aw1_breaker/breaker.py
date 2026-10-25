import ast
import base64
import hashlib
import hmac
import os
import secrets
import time
from typing import Dict, Any, Tuple

AW1_SECRET_KEY = os.environ.get("AW1_BREAKER_SECRET", "aw1-sovereign-circuit-breaker-key-2026").encode("utf-8")

class ASTSymbolicUnpacker:
    """Zero-dependency Abstract Syntax Tree unpacker and danger analyzer."""
    DANGEROUS_PRIMITIVES = {
        "os.system", "subprocess.Popen", "subprocess.run", "subprocess.call",
        "shutil.rmtree", "eval", "exec", "__import__", "socket.socket",
        "requests.post", "urllib.request", "paramiko"
    }

    @classmethod
    def unpack_and_scan(cls, payload: str) -> Tuple[bool, str, list]:
        raw_code = payload
        if payload.startswith("base64:"):
            try:
                raw_code = base64.b64decode(payload[7:]).decode("utf-8", errors="ignore")
            except Exception as e:
                return False, f"Base64 decode failure: {e}", []

        markers = []
        try:
            tree = ast.parse(raw_code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in cls.DANGEROUS_PRIMITIVES:
                        markers.append(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        val = node.func.value
                        attr = node.func.attr
                        if isinstance(val, ast.Name):
                            full_name = f"{val.id}.{attr}"
                            if full_name in cls.DANGEROUS_PRIMITIVES:
                                markers.append(full_name)
                elif isinstance(node, ast.Import):
                    for n in node.names:
                        if n.name in {"os", "subprocess", "socket", "paramiko"}:
                            markers.append(f"import:{n.name}")
        except Exception:
            for p in cls.DANGEROUS_PRIMITIVES:
                if p in raw_code:
                    markers.append(p)

        is_safe = len(markers) == 0
        return is_safe, raw_code, markers


class StatefulCausalMemory:
    """In-memory rolling per-actor velocity and transaction amount monitor."""
    def __init__(self, window_days: int = 30):
        self.window_seconds = window_days * 86400
        self.actor_logs: Dict[str, list] = {}

    def check_velocity(self, actor_id: str, amount: float, baseline: float = 100000.0) -> Tuple[bool, str]:
        now = time.time()
        if actor_id not in self.actor_logs:
            self.actor_logs[actor_id] = []

        self.actor_logs[actor_id] = [(ts, amt) for ts, amt in self.actor_logs[actor_id] if now - ts <= self.window_seconds]
        cumulative = sum(amt for _, amt in self.actor_logs[actor_id]) + amount
        ratio = cumulative / baseline if baseline > 0 else 1.0

        if ratio > 1.0:
            return False, f"VELOCITY_SPIKE_DETECTED (ratio={ratio:.2f} > 1.0, cumulative={cumulative:,.2f})"

        self.actor_logs[actor_id].append((now, amount))
        return True, "VELOCITY_NORMAL"


class ExecutionBreaker:
    """Autonomous Agent Out-of-Band AST Interception Gateway."""
    memory = StatefulCausalMemory()

    @classmethod
    def generate_signed_token(cls, actor_id: str) -> str:
        token_nonce = secrets.token_hex(8)
        ts = int(time.time())
        sig_body = f"{token_nonce}:{actor_id}:{ts}".encode("utf-8")
        signature = hmac.new(AW1_SECRET_KEY, sig_body, hashlib.sha256).hexdigest()[:16]
        return f"AW1-EXEC-TOKEN-{token_nonce}.{ts}.{signature}"

    @classmethod
    def verify_execution_token(cls, token: str, actor_id: str, max_age_seconds: int = 300) -> bool:
        try:
            if not token.startswith("AW1-EXEC-TOKEN-"):
                return False
            clean = token[len("AW1-EXEC-TOKEN-"):]
            parts = clean.split(".")
            if len(parts) != 3:
                return False
            token_nonce, ts_str, signature = parts
            ts = int(ts_str)
            if time.time() - ts > max_age_seconds:
                return False
            sig_body = f"{token_nonce}:{actor_id}:{ts}".encode("utf-8")
            expected_sig = hmac.new(AW1_SECRET_KEY, sig_body, hashlib.sha256).hexdigest()[:16]
            return hmac.compare_digest(signature, expected_sig)
        except Exception:
            return False

    @classmethod
    def intercept(cls, actor_id: str, tool_name: str, payload: str, amount: float = 0.0) -> Dict[str, Any]:
        t0 = time.perf_counter()

        is_safe, unpacked_code, markers = ASTSymbolicUnpacker.unpack_and_scan(payload)
        if not is_safe:
            lat_ms = (time.perf_counter() - t0) * 1000
            digest = hashlib.sha256(f"{actor_id}{tool_name}{payload}{lat_ms}".encode()).hexdigest()
            return {
                "decision": "HALT_AND_CONTAIN",
                "reason": f"DANGEROUS_PRIMITIVES_DETECTED: {', '.join(markers)}",
                "latency_ms": round(lat_ms, 4),
                "sha256_digest": digest,
                "token": None
            }

        if amount > 0:
            ok_vel, vel_reason = cls.memory.check_velocity(actor_id, amount)
            if not ok_vel:
                lat_ms = (time.perf_counter() - t0) * 1000
                digest = hashlib.sha256(f"{actor_id}{tool_name}{amount}{lat_ms}".encode()).hexdigest()
                return {
                    "decision": "HALT_AND_CONTAIN",
                    "reason": vel_reason,
                    "latency_ms": round(lat_ms, 4),
                    "sha256_digest": digest,
                    "token": None
                }

        lat_ms = (time.perf_counter() - t0) * 1000
        signed_token = cls.generate_signed_token(actor_id)
        digest = hashlib.sha256(f"{signed_token}{actor_id}{tool_name}".encode()).hexdigest()

        return {
            "decision": "PERMITTED",
            "reason": "AST_PRIMITIVES_CLEARED_AND_VELOCITY_VALIDATED",
            "latency_ms": round(lat_ms, 4),
            "sha256_digest": digest,
            "token": signed_token
        }
