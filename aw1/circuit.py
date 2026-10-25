import time
import secrets
import hashlib
from typing import Dict, Any, Optional, List
from aw1.unpacker import ASTSymbolicUnpacker
from aw1.memory import StatefulCausalMemory
from aw1.models import Verdict
from aw1.policy import PolicyConfig
from aw1.parsers.sql_guard import SQLGuard
from aw1.parsers.shell_guard import ShellGuard

class ExecutionBreaker:
    """
    Out-of-band execution circuit breaker governing autonomous agent tool calls.
    """
    DANGEROUS_PRIMITIVES = {
        "[CODE_EVAL_POLYGLOT]",
        "[NETWORK_EGRESS]",
        "[SYSTEM_SHELL_EXEC]",
        "[KERNEL_WRITE]",
        "[DYNAMIC_EVAL]",
        "[CORRUPT_DYNAMIC_EVAL]",
        "[UNSAFE_EXECUTION_TUNNEL]"
    }

    def __init__(self, baseline_velocity: float = 50000.0, policy: Optional[PolicyConfig] = None):
        self.unpacker = ASTSymbolicUnpacker()
        self.memory = StatefulCausalMemory(baseline_velocity_limit=baseline_velocity)
        self.policy = policy or PolicyConfig()

    def intercept(self, actor_id: str, tool_name: str, payload: str, amount: float = 0.0) -> Verdict:
        start_time = time.perf_counter()
        # Pre-flight Guard 0: Base64 obfuscation & corruption inspection
        payload_str = str(payload).strip()
        if payload_str.startswith("base64:") or "base64:" in payload_str:
            import base64
            import binascii
            b64_part = payload_str.split("base64:", 1)[1].strip()
            try:
                decoded_bytes = base64.b64decode(b64_part, validate=True)
                payload = decoded_bytes.decode('utf-8', errors='ignore')
            except (binascii.Error, ValueError) as b64_err:
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                dossier_data = f"{actor_id}:{tool_name}:{payload}:CORRUPT_BASE64:{time.time()}"
                return Verdict(
                    decision="🛑 HALT_AND_CONTAIN",
                    status="HALT_AND_CONTAIN",
                    containment_reason=f"CORRUPT_DYNAMIC_EVAL: Malformed or unparseable base64 payload ({b64_err})",
                    ast_primitives=["[CORRUPT_DYNAMIC_EVAL]", "[DYNAMIC_EVAL]"],
                    latency_ms=round(latency_ms, 4),
                    sha256_dossier=hashlib.sha256(dossier_data.encode()).hexdigest(),
                    token=None
                )

        # Pre-flight Guard 1: SQL syntax analysis
        if self.policy.strict_sql:
            sql_hit = SQLGuard.inspect(payload)
            if sql_hit:
                prim, reason = sql_hit
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                dossier_data = f"{actor_id}:{tool_name}:{payload}:BLOCKED_SQL:{time.time()}"
                sha256_hash = hashlib.sha256(dossier_data.encode()).hexdigest()
                return Verdict(
                    decision="🛑 HALT_AND_CONTAIN",
                    status="HALT_AND_CONTAIN",
                    containment_reason=reason,
                    ast_primitives=[prim],
                    latency_ms=round(latency_ms, 4),
                    sha256_dossier=sha256_hash,
                    token=None
                )

        # Pre-flight Guard 2: Shell pipe & CLI analysis
        if self.policy.strict_shell:
            shell_hit = ShellGuard.inspect(payload)
            if shell_hit:
                prim, reason = shell_hit
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                dossier_data = f"{actor_id}:{tool_name}:{payload}:BLOCKED_SHELL:{time.time()}"
                sha256_hash = hashlib.sha256(dossier_data.encode()).hexdigest()
                return Verdict(
                    decision="🛑 HALT_AND_CONTAIN",
                    status="HALT_AND_CONTAIN",
                    containment_reason=reason,
                    ast_primitives=[prim],
                    latency_ms=round(latency_ms, 4),
                    sha256_dossier=sha256_hash,
                    token=None
                )

        # Pre-flight Guard 3: Configurable Domain Policy Targets
        lower_payload = payload.lower()
        matched_target = any(t in lower_payload for t in self.policy.critical_targets)
        matched_action = any(a in lower_payload for a in self.policy.restricted_actions)
        if matched_target and matched_action:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            dossier_data = f"{actor_id}:{tool_name}:{payload}:BLOCKED_POLICY:{time.time()}"
            sha256_hash = hashlib.sha256(dossier_data.encode()).hexdigest()
            return Verdict(
                decision="🛑 HALT_AND_CONTAIN",
                status="HALT_AND_CONTAIN",
                containment_reason="Policy violation: restricted action targeting protected domain entity",
                ast_primitives=["[DOMAIN_POLICY_CONTAINMENT]"],
                latency_ms=round(latency_ms, 4),
                sha256_dossier=sha256_hash,
                token=None
            )

        # Layer 0: Decompile AST Primitives
        primitives, raw_unpacked = self.unpacker.decompile(payload)

        # Check for AST-level injection or dangerous execution primitives
        blocked_primitives = [p for p in primitives if p in self.DANGEROUS_PRIMITIVES]
        if blocked_primitives:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            dossier_data = f"{actor_id}:{tool_name}:{payload}:BLOCKED:{time.time()}"
            sha256_hash = hashlib.sha256(dossier_data.encode()).hexdigest()
            return Verdict(
                decision="🛑 HALT_AND_CONTAIN",
                status="HALT_AND_CONTAIN",
                containment_reason=f"CRITICAL_AST_PRIMITIVE_DETECTED ({', '.join(blocked_primitives)})",
                ast_primitives=primitives,
                latency_ms=round(latency_ms, 4),
                sha256_dossier=sha256_hash,
                token=None
            )

        # Layer 1: Stateful Velocity Check
        allowed, ratio, reason = self.memory.record_and_evaluate(actor_id, amount)
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        # Decision Assurance Dossier Hash
        dossier_data = f"{actor_id}:{tool_name}:{payload}:{allowed}:{time.time()}"
        sha256_hash = hashlib.sha256(dossier_data.encode()).hexdigest()

        if not allowed:
            return Verdict(
                decision="🛑 HALT_AND_CONTAIN",
                status="HALT_AND_CONTAIN",
                containment_reason=reason,
                ast_primitives=primitives,
                latency_ms=round(latency_ms, 4),
                sha256_dossier=sha256_hash,
                token=None
            )

        # Gate 7: Permitted Execution Token Generation
        token = f"AW1-EXEC-TOKEN-{secrets.token_hex(8)}"
        return Verdict(
            decision="APPROVED_PROCEED",
            status="PERMITTED",
            containment_reason="CLEAR",
            ast_primitives=primitives,
            latency_ms=round(latency_ms, 4),
            sha256_dossier=sha256_hash,
            token=token
        )

ASTCircuitBreaker = ExecutionBreaker
