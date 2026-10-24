"""
aw1_breaker/adapters.py
Zero-Friction Drop-in Adapters for LangGraph, CrewAI, and LlamaIndex.
"""
from functools import wraps
from typing import Callable, Any, Dict
from .cli import scan_code_ast

class CircuitBreakerException(PermissionError):
    """Raised when an autonomous agent attempts a restricted action."""
    pass

# ==============================================================================
# 1. LangChain / LangGraph Adapter
# ==============================================================================
def guard_agent_action(tool_name: str = "generic_tool"):
    """
    Decorator for LangGraph tool nodes.
    Usage:
        @guard_agent_action(tool_name="bash_executor")
        def run_shell(command: str):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract serialized argument payload
            payload = " ".join([str(a) for a in args]) + " " + " ".join([f"{k}={v}" for k, v in kwargs.items()])
            is_permitted, reason, lat = scan_code_ast(payload)
            if not is_permitted:
                raise CircuitBreakerException(
                    f"[AW-1 GATE 7 HALT] Tool '{tool_name}' blocked in {lat:.4f}ms. Violation: {reason}"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ==============================================================================
# 2. CrewAI & AutoGen Interceptor
# ==============================================================================
class AW1CrewAIGuard:
    """
    Hook for CrewAI tool execution callbacks.
    Usage:
        guard = AW1CrewAIGuard()
        crew = Crew(agents=[...], tasks=[...], step_callback=guard.intercept_step)
    """
    @staticmethod
    def intercept_step(step_output: Any):
        raw_cmd = str(step_output)
        is_permitted, reason, lat = scan_code_ast(raw_cmd)
        if not is_permitted:
            raise CircuitBreakerException(
                f"[AW-1 GATE 7 TRIPPED] Autonomous agent containment activated ({lat:.4f}ms). Reason: {reason}"
            )
        return True

# ==============================================================================
# 3. LlamaIndex Tool Call Gate
# ==============================================================================
class AW1LlamaIndexInterceptor:
    """
    Tool runner interceptor for LlamaIndex query engines.
    """
    @staticmethod
    def validate_tool_call(tool_name: str, tool_kwargs: Dict[str, Any]) -> bool:
        serialized = " ".join([f"{k}={v}" for k, v in tool_kwargs.items()])
        is_permitted, reason, lat = scan_code_ast(serialized)
        if not is_permitted:
            raise CircuitBreakerException(
                f"[AW-1 INTERCEPTOR] LlamaIndex tool call '{tool_name}' rejected ({lat:.4f}ms): {reason}"
            )
        return True
