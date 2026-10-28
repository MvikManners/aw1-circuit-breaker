import json
from typing import Dict, Any, Callable, Optional
from aw1.circuit import ExecutionBreaker

def _extract_val(obj, key, default=None):
    if hasattr(obj, key):
        val = getattr(obj, key)
        if val is not None:
            return val
    if isinstance(obj, dict) or hasattr(obj, "__getitem__"):
        try:
            val = obj[key]
            if val is not None:
                return val
        except (KeyError, TypeError, IndexError):
            pass
    return default

class AW1MCPInterceptor:
    """
    Model Context Protocol (MCP) execution circuit breaker proxy.
    Wraps standard tools/call requests before dispatching to shell/DB sockets.
    """
    def __init__(self, baseline_velocity: float = 50000.0):
        self.breaker = ExecutionBreaker(baseline_velocity=baseline_velocity)

    def intercept_mcp_request(
        self,
        request: Dict[str, Any],
        actor_id: str = "mcp_agent_default",
        execution_handler: Optional[Callable[..., Any]] = None
    ) -> Dict[str, Any]:
        """
        Intercepts an incoming MCP 'tools/call' JSON-RPC payload.
        """
        method = request.get("method")
        
        # Pass non-execution methods straight through (e.g. tools/list, resources/read)
        if method != "tools/call":
            if execution_handler:
                return execution_handler(request)
            return {"status": "PASSED_THROUGH", "request": request}

        params = request.get("params", {})
        tool_name = params.get("name", "unknown_tool")
        arguments = params.get("arguments", {})
        
        payload_str = json.dumps(arguments)
        
        # Extract value/amount if present in arguments
        amount = 0.0
        for key in ["amount", "value", "payout", "funds"]:
            if key in arguments:
                try:
                    amount = float(arguments[key])
                    break
                except (ValueError, TypeError):
                    pass

        # Circuit Breaker Interception
        verdict = self.breaker.intercept(
            actor_id=actor_id,
            tool_name=tool_name,
            payload=payload_str,
            amount=amount
        )

        status = _extract_val(verdict, "status", "")
        decision = _extract_val(verdict, "decision", "")
        token = _extract_val(verdict, "token", None)

        # Zero-Trust Fail-Closed rule:
        # Block if explicitly halted/contained, or if an execution token was not minted
        is_blocked = (
            status in ("BLOCKED", "HALT", "HALT_AND_CONTAIN") or
            "HALT" in str(decision) or
            "CONTAIN" in str(decision) or
            token is None
        )

        if is_blocked:
            reason = (
                _extract_val(verdict, "containment_reason") or
                _extract_val(verdict, "reason") or
                "Zero-Trust containment triggered"
            )
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32000,
                    "message": "EXECUTION_REVOKED_BY_CIRCUIT_BREAKER",
                    "data": {
                        "status": status,
                        "containment_reason": reason,
                        "ast_primitives": _extract_val(verdict, "ast_primitives", []),
                        "latency_ms": _extract_val(verdict, "latency_ms", 0.0),
                        "sha256_dossier": _extract_val(verdict, "sha256_dossier", "") or _extract_val(verdict, "dossier_hash", "")
                    }
                }
            }

        # Approved: Forward request with execution token
        if execution_handler:
            return execution_handler(request, execution_token=token)

        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "status": "APPROVED",
                "token": token,
                "latency_ms": _extract_val(verdict, "latency_ms", 0.0),
                "sha256_dossier": _extract_val(verdict, "sha256_dossier", "") or _extract_val(verdict, "dossier_hash", "")
            }
        }
