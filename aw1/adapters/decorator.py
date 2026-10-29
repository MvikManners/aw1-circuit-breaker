import functools
from typing import Callable, Any
from aw1.circuit import ASTCircuitBreaker
from aw1.models import Verdict

_DEFAULT_BREAKER = None

def get_default_breaker() -> ASTCircuitBreaker:
    global _DEFAULT_BREAKER
    if _DEFAULT_BREAKER is None:
        _DEFAULT_BREAKER = ASTCircuitBreaker()
    return _DEFAULT_BREAKER

def protect_tool(actor_id: str = "agent", breaker: ASTCircuitBreaker = None):
    """
    Drop-in decorator for agent tools:
    @protect_tool()
    def my_tool(command: str): ...
    """
    def decorator(func: Callable) -> Callable:
        cb = breaker or get_default_breaker()
        tool_name = func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Extract first string argument as target payload
            payload_candidates = [a for a in args if isinstance(a, str)] + \
                                 [v for v in kwargs.values() if isinstance(v, str)]
            payload = payload_candidates[0] if payload_candidates else ""

            verdict: Verdict = cb.intercept(actor_id=actor_id, tool_name=tool_name, payload=payload)
            if verdict.is_contained:
                raise PermissionError(f"[AW-1 CONTAINMENT] Execution blocked: {verdict.containment_reason} (Token: {verdict.token})")

            return func(*args, **kwargs)
        return wrapper
    return decorator
