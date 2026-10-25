import ast
import time
import json
import inspect
import functools
import logging
from typing import Any, Callable, Dict, Optional, Union

logger = logging.getLogger("aw1.circuit")

_DEFAULT_BREAKER = None

def get_default_breaker():
    global _DEFAULT_BREAKER
    if _DEFAULT_BREAKER is None:
        try:
            from aw1.circuit import ASTCircuitBreaker
            _DEFAULT_BREAKER = ASTCircuitBreaker()
        except Exception:
            _DEFAULT_BREAKER = None
    return _DEFAULT_BREAKER

def _emit_telemetry(verdict: str, callable_name: str, latency_ms: float, reason: Optional[str] = None, payload_sample: Optional[str] = None) -> dict:
    event = {
        "event": "aw1_arbitration",
        "timestamp_epoch": time.time(),
        "target": callable_name,
        "verdict": verdict,
        "latency_ms": round(latency_ms, 4),
        "reason": reason or "AST verification passed",
        "payload_sample": payload_sample[:120] if payload_sample else None
    }
    log_line = json.dumps(event)
    if verdict == "FAIL_CLOSED":
        logger.warning(log_line)
    else:
        logger.info(log_line)
    return event

def _inspect_ast_safety(code_str: str) -> tuple[bool, Optional[str]]:
    """Evaluates payload against the active enterprise policy engine."""
    from aw1.policy import get_active_policy
    return get_active_policy().inspect_ast(code_str)

def guard(target: Optional[Union[Callable, str]] = None, *, fail_closed: bool = True):
    """
    Universal AW-1 circuit breaker decorator.
    Supports standard synchronous functions, async coroutines, and tool-call payload handlers.
    """
    def decorator(fn: Callable) -> Callable:
        callable_name = f"{fn.__module__}.{fn.__qualname__}"

        def _evaluate_args(args: tuple, kwargs: dict) -> tuple[bool, float, Optional[str], Optional[str]]:
            start = time.perf_counter()
            candidate_payload = None

            for arg in args:
                if isinstance(arg, str):
                    candidate_payload = arg
                    break
                elif isinstance(arg, dict):
                    if "code" in arg:
                        candidate_payload = str(arg["code"])
                        break
                    elif "arguments" in arg:
                        candidate_payload = str(arg["arguments"])
                        break

            if candidate_payload is None:
                for k, v in kwargs.items():
                    if isinstance(v, str) and k in {"code", "command", "script", "query", "arguments"}:
                        candidate_payload = v
                        break
                    elif isinstance(v, dict) and k in {"tool_call", "payload", "action"}:
                        if "arguments" in v:
                            candidate_payload = str(v["arguments"])
                            break
                        elif "code" in v:
                            candidate_payload = str(v["code"])
                            break

            if candidate_payload:
                is_safe, reason = _inspect_ast_safety(candidate_payload)
                latency_ms = (time.perf_counter() - start) * 1000.0
                return is_safe, latency_ms, reason, candidate_payload

            latency_ms = (time.perf_counter() - start) * 1000.0
            return True, latency_ms, None, None

        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(*args, **kwargs):
                is_safe, latency_ms, reason, sample = _evaluate_args(args, kwargs)
                if not is_safe:
                    _emit_telemetry("FAIL_CLOSED", callable_name, latency_ms, reason, sample)
                    if fail_closed:
                        raise PermissionError(f"[AW-1 BREAKER TRIPPED] Execution blocked: {reason}")
                    return {"error": "AW-1 circuit breaker blocked execution", "reason": reason}

                _emit_telemetry("PASS", callable_name, latency_ms, None, sample)
                return await fn(*args, **kwargs)
            return async_wrapper
        else:
            @functools.wraps(fn)
            def sync_wrapper(*args, **kwargs):
                is_safe, latency_ms, reason, sample = _evaluate_args(args, kwargs)
                if not is_safe:
                    _emit_telemetry("FAIL_CLOSED", callable_name, latency_ms, reason, sample)
                    if fail_closed:
                        raise PermissionError(f"[AW-1 BREAKER TRIPPED] Execution blocked: {reason}")
                    return {"error": "AW-1 circuit breaker blocked execution", "reason": reason}

                _emit_telemetry("PASS", callable_name, latency_ms, None, sample)
                return fn(*args, **kwargs)
            return sync_wrapper

    if callable(target):
        return decorator(target)
    return decorator

def protect_tool(*args, **kwargs):
    """Backward-compatible wrapper for legacy protect_tool usage."""
    if args and callable(args[0]):
        return guard(args[0])
    return guard(fail_closed=kwargs.get("fail_closed", True))
