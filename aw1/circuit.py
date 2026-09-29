import time
import secrets
import hashlib
from typing import Dict, Any, Optional
from aw1.unpacker import ASTSymbolicUnpacker
from aw1.memory import StatefulCausalMemory

class ExecutionBreaker:
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
        start_time = time.perf_counter()
        
        # Layer 0: Decompile AST Primitives
        primitives, raw_unpacked = self.unpacker.decompile(payload)
        
        # Check for AST-level injection or dangerous execution primitives
        blocked_primitives = [p for p in primitives if p in self.DANGEROUS_PRIMITIVES]
        if blocked_primitives:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            dossier_data = f"{actor_id}:{tool_name}:{payload}:BLOCKED:{time.time()}"
            sha256_hash = hashlib.sha256(dossier_data.encode()).hexdigest()
            return {
                "decision": "🛑 HALT_AND_CONTAIN",
                "status": "HALT_AND_CONTAIN",
                "containment_reason": f"CRITICAL_AST_PRIMITIVE_DETECTED ({", ".join(blocked_primitives)})",
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
        token = f"AW1-EXEC-TOKEN-{secrets.token_hex(8)}"
        return {
            "decision": "APPROVED_PROCEED",
            "status": "PERMITTED",
            "containment_reason": "CLEAR",
            "ast_primitives": primitives,
            "latency_ms": round(latency_ms, 4),
            "sha256_dossier": sha256_hash,
            "token": token
        }
