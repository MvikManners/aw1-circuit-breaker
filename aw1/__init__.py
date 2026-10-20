"""
LAVETO WISDOM (AW-1) — Production Execution Circuit Breaker
Out-of-band deterministic runtime safety for autonomous agents.
"""

from functools import wraps
from typing import Any, Callable
import asyncio

from aw1.circuit import ExecutionBreaker
from aw1.unpacker import ASTSymbolicUnpacker
from aw1.memory import StatefulCausalMemory
from aw1.mcp_proxy import AW1MCPInterceptor
from aw1.reversibility import ReversibilityRouter, DoorType, ReversibilityDecision
from aw1.dossier import DecisionAssuranceDossier, AssuranceEngine
from aw1.regulatory import RegulatoryComplianceEngine, StatutoryStandard
from aw1.trust_reconciliation import TrustAccountReconciliationEngine

# Backwards compatibility alias
MCPContractGuard = AW1MCPInterceptor



def wrap_agent_tool(breaker: ExecutionBreaker, actor: str = 'agent_worker'):
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for arg in list(args) + list(kwargs.values()):
                if isinstance(arg, str):
                    breaker.inspect_payload(arg, actor=actor)
            return func(*args, **kwargs)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            for arg in list(args) + list(kwargs.values()):
                if isinstance(arg, str):
                    breaker.inspect_payload(arg, actor=actor)
            return await func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper

    return decorator

__all__ = [
    'ASTCircuitBreaker',
    'ExecutionBreaker',
    'ASTSymbolicUnpacker',
    'StatefulCausalMemory',
    'AW1MCPInterceptor',
    'MCPContractGuard',
    'wrap_agent_tool',
    'ReversibilityRouter',
    'DoorType',
    'ReversibilityDecision',
    'DecisionAssuranceDossier',
    'AssuranceEngine',
    'RegulatoryComplianceEngine',
    'StatutoryStandard',
    'TrustAccountReconciliationEngine',
]


# Public API Canonical Alias
ASTCircuitBreaker = ExecutionBreaker


# --- AW-1 v0.2.0 Enterprise Extensions ---
from aw1.models import Verdict
from aw1.policy import PolicyConfig
from aw1.adapters import protect_tool

__version__ = "0.2.1"

# Extend __all__ if present
try:
    __all__ = list(__all__) + ["Verdict", "PolicyConfig", "protect_tool"]
except NameError:
    __all__ = ["ASTCircuitBreaker", "ExecutionBreaker", "Verdict", "PolicyConfig", "protect_tool"]

from aw1.guard import EnterpriseGuard, SecurityViolationError

from aw1.adapters.decorator import guard
