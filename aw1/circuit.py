import os, base64, hmac, hashlib, time, secrets
AW1_SECRET_KEY = os.environ.get("AW1_BREAKER_SECRET", "aw1-sovereign-circuit-breaker-key-2026").encode("utf-8")
import time
import secrets
import hashlib
from typing import Dict, Any, Optional
from aw1.unpacker import ASTSymbolicUnpacker
from aw1.memory import StatefulCausalMemory

class ExecutionBreaker:
    _inst = None
    @classmethod
    def _get_inst(cls):
        if cls._inst is None: cls._inst = cls()
        return cls._inst

    @classmethod
    def generate_signed_token(cls, actor_id: str) -> str:
        nonce, ts = secrets.token_hex(8), int(time.time())
        sig = hmac.new(AW1_SECRET_KEY, f"{nonce}:{actor_id}:{ts}".encode(), hashlib.sha256).hexdigest()[:16]
        return f"AW1-EXEC-TOKEN-{nonce}.{ts}.{sig}"

    @classmethod
    def verify_execution_token(cls, token: str, actor_id: str, max_age: int = 300) -> bool:
        try:
            if not token or not token.startswith("AW1-EXEC-TOKEN-"): return False
            nonce, ts_str, sig = token[15:].split(".")
            if time.time() - int(ts_str) > max_age: return False
            exp = hmac.new(AW1_SECRET_KEY, f"{nonce}:{actor_id}:{ts_str}".encode(), hashlib.sha256).hexdigest()[:16]
            return hmac.compare_digest(sig, exp)
        except Exception: return False

    """
    Out-of-band execution circuit breaker governing autonomous agent tool calls.
    """
    DANGEROUS_PRIMITIVES = {
        "[CODE_EVAL_POLYGLOT]",
        "[HIGH_VALUE_ONE_WAY_DOOR]",
        "[NETWORK_EGRESS]",
        "[SYSTEM_SHELL_EXEC]",
        "[KERNEL_WRITE]"
    }

    def __init__(self, baseline_velocity: float = 50000.0):
        self.unpacker = ASTSymbolicUnpacker()
        self.memory = StatefulCausalMemory(baseline_velocity_limit=baseline_velocity)

    def intercept(self, actor_id: str, tool_name: str, payload: str, amount: float = 0.0) -> Dict[str, Any]:
        if not isinstance(self, ExecutionBreaker):
            return ExecutionBreaker._get_inst().intercept(self, actor_id, tool_name, payload)
        start_time = time.perf_counter()
        
        # Layer 0: Decompile AST Primitives
        # Layer 0: Decode base64 payload prefix if present
        scan_payload = payload
        if isinstance(scan_payload, str) and scan_payload.startswith("base64:"):
            try:
                scan_payload = base64.b64decode(scan_payload[7:]).decode("utf-8", errors="ignore")
            except Exception:
                pass

        primitives, raw_unpacked = self.unpacker.decompile(scan_payload)
        
        # Check for AST-level injection or dangerous execution primitives
        blocked_primitives = [p for p in primitives if p in self.DANGEROUS_PRIMITIVES]
        if blocked_primitives:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            dossier_data = f"{actor_id}:{tool_name}:{payload}:BLOCKED:{time.time()}"
            sha256_hash = hashlib.sha256(dossier_data.encode()).hexdigest()
            return {
                "decision": "🛑 HALT_AND_CONTAIN",
                "status": "HALT_AND_CONTAIN",
                "containment_reason": f"CRITICAL_AST_PRIMITIVE_DETECTED ({', '.join(blocked_primitives)})",
                "ast_primitives": primitives,
                "latency_ms": round(latency_ms, 4),
                "sha256_dossier": sha256_hash,
                "token": None
            }

        # Layer 1: Stateful Velocity Check
        allowed, ratio, reason = self.memory.record_and_evaluate(actor_id, amount)
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        
        # Decision Assurance Dossier Hash
        dossier_data = f"{actor_id}:{tool_name}:{payload}:{allowed}:{time.time()}"
        sha256_hash = hashlib.sha256(dossier_data.encode()).hexdigest()

        if not allowed:
            return {
                "decision": "🛑 HALT_AND_CONTAIN",
                "status": "HALT_AND_CONTAIN",
                "containment_reason": reason,
                "ast_primitives": primitives,
                "latency_ms": round(latency_ms, 4),
                "sha256_dossier": sha256_hash,
                "token": None
            }

        # Gate 7: Permitted Execution Token Generation
        token = self.generate_signed_token(actor_id)
        return {
            "decision": "APPROVED_PROCEED",
            "status": "PERMITTED",
            "containment_reason": "CLEAR",
            "ast_primitives": primitives,
            "latency_ms": round(latency_ms, 4),
            "sha256_dossier": sha256_hash,
            "token": token
        }
