"""
aw1.guard - Turnkey Enterprise Policy & Execution Guard
Deterministic out-of-band security wrapper for AI agent tool dispatch.
"""
import time, functools, hashlib
from typing import Dict, List, Optional, Callable, Any
from aw1.circuit import ExecutionBreaker

class SecurityViolationError(PermissionError):
    """Raised when an autonomous agent violates enterprise security or policy bounds."""
    def __init__(self, message: str, audit_receipt: dict):
        super().__init__(message)
        self.audit_receipt = audit_receipt

class EnterpriseGuard:
    """
    Enterprise Policy Guard that combines:
    1. Tool whitelisting
    2. Rolling per-actor velocity throttling
    3. Fiduciary financial transaction caps
    4. Deterministic SQL read-only inspection
    5. Layer-0 AST deconstruction via ExecutionBreaker
    6. HMAC-SHA256 cryptographic execution tokens
    """
    def __init__(
        self,
        allowed_tools: Optional[List[str]] = None,
        max_velocity_per_min: int = 60,
        max_financial_limit: float = 500.0,
        readonly_sql: bool = True
    ):
        self.allowed_tools = set(allowed_tools) if allowed_tools else None
        self.max_velocity_per_min = max_velocity_per_min
        self.max_financial_limit = max_financial_limit
        self.readonly_sql = readonly_sql
        self._velocity_ledger: Dict[str, List[float]] = {}
        self.breaker = ExecutionBreaker()

    def audit_and_verify(
        self,
        actor_id: str,
        tool_name: str,
        payload: Any,
        cost: float = 0.0
    ) -> dict:
        now = time.time()

        # 1. Tool Whitelist Check
        if self.allowed_tools is not None and tool_name not in self.allowed_tools:
            return self._create_receipt(actor_id, tool_name, payload, cost, "HALT_UNAUTHORIZED_TOOL", f"Tool '{tool_name}' not in allowed enterprise whitelist")

        # 2. Rolling Velocity Throttling
        timestamps = [t for t in self._velocity_ledger.get(actor_id, []) if now - t < 60.0]
        if len(timestamps) >= self.max_velocity_per_min:
            return self._create_receipt(actor_id, tool_name, payload, cost, "HALT_VELOCITY_EXCEEDED", f"Rate limit exceeded: {len(timestamps)} calls in 60s (max {self.max_velocity_per_min})")
        timestamps.append(now)
        self._velocity_ledger[actor_id] = timestamps

        # 3. Fiduciary Financial Cap
        if cost > self.max_financial_limit:
            return self._create_receipt(actor_id, tool_name, payload, cost, "HALT_FINANCIAL_CAP_EXCEEDED", f"Cost {cost:.2f} exceeds policy maximum of {self.max_financial_limit:.2f}")

        # 4. SQL Mutation Gate
        payload_str = str(payload)
        if self.readonly_sql and any(kw in tool_name.lower() for kw in ["sql", "query", "db", "database"]):
            forbidden = ["DROP ", "DELETE ", "TRUNCATE ", "ALTER ", "UPDATE ", "INSERT "]
            if any(fkw in payload_str.upper() for fkw in forbidden):
                return self._create_receipt(actor_id, tool_name, payload, cost, "HALT_SQL_MUTATION_FORBIDDEN", "Database mutation rejected under readonly_sql policy")

        # 5. Core AST Circuit Breaker Interception
        intercept_res = self.breaker.intercept(actor_id, tool_name, payload_str, cost)
        decision = intercept_res.get("decision", "")
        if "HALT" in decision:
            return self._create_receipt(actor_id, tool_name, payload, cost, decision, intercept_res.get("reason", "Malicious AST primitive detected"))

        # 6. Approved: Issue signed receipt with execution token
        receipt = self._create_receipt(actor_id, tool_name, payload, cost, "APPROVED_PROCEED", "Passed enterprise policy and AST circuit breaker")
        receipt["token"] = intercept_res.get("token")
        return receipt

    def protect(self, tool_name: Optional[str] = None, cost: float = 0.0):
        """1-Line decorator to protect any Python agent tool function."""
        def decorator(fn: Callable):
            name = tool_name or fn.__name__
            @functools.wraps(fn)
            def wrapper(*args, actor_id: str = "agent-core", **kwargs):
                payload = {"args": args, "kwargs": kwargs} if (args or kwargs) else ""
                receipt = self.audit_and_verify(actor_id, name, payload, cost)
                if receipt["decision"] != "APPROVED_PROCEED":
                    raise SecurityViolationError(f"Execution halted by EnterpriseGuard: {receipt['reason']}", receipt)
                return fn(*args, **kwargs)
            return wrapper
        return decorator

    def _create_receipt(self, actor: str, tool: str, payload: Any, cost: float, decision: str, reason: str) -> dict:
        ts = time.time()
        raw_str = f"{actor}:{tool}:{payload}:{cost}:{decision}:{ts}"
        sha_seal = hashlib.sha256(raw_str.encode()).hexdigest()
        return {
            "timestamp": ts,
            "actor_id": actor,
            "tool_name": tool,
            "decision": decision,
            "reason": reason,
            "cost": cost,
            "sha256_seal": sha_seal
        }
