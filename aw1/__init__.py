"""
LAVETO WISDOM (AW-1) — Production Execution Circuit Breaker
Out-of-band deterministic runtime safety for autonomous agents.
"""

from functools import wraps
from typing import Any, Callable
import asyncio

from aw1.circuit import ExecutionBreaker
from aw1.unpacker import ASTSymbolicUnpacker, ConstantFolder
from aw1.memory import StatefulCausalMemory, InMemoryMemoryBackend, RedisMemoryBackend
from aw1.mcp_guard import MCPContractGuard
from aw1.reversibility import ReversibilityRouter, DoorType, ReversibilityDecision
from aw1.dossier import DecisionAssuranceDossier, AssuranceEngine
from aw1.regulatory import RegulatoryComplianceEngine, StatutoryStandard

# Backwards compatibility alias
AW1MCPInterceptor = MCPContractGuard

__version__ = "0.2.0"


def wrap_agent_tool(breaker: ExecutionBreaker, actor: str = "agent_worker"):
    """
    Zero-dependency wrapper for LangChain @tool, CrewAI tools, or custom callables.
    Evaluates AST execution paths deterministically prior to invoking the underlying tool.
    """
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
    "ExecutionBreaker",
    "ASTSymbolicUnpacker",
    "ConstantFolder",
    "StatefulCausalMemory",
    "InMemoryMemoryBackend",
    "RedisMemoryBackend",
    "MCPContractGuard",
    "AW1MCPInterceptor",
    "wrap_agent_tool",
    "ReversibilityRouter",
    "DoorType",
    "ReversibilityDecision",
    "DecisionAssuranceDossier",
    "AssuranceEngine",
    "RegulatoryComplianceEngine",
    "StatutoryStandard",
]
