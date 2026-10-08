import json
from typing import Dict, Any, Callable, Optional
from aw1.circuit import ExecutionBreaker

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
        execution_handler: Optional[Callable[[Dict[str, Any]], Any]] = None
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
        
        # Serialize arguments to inspect primitives
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

        if verdict["status"] == "BLOCKED":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32000,
                    "message": "EXECUTION_REVOKED_BY_CIRCUIT_BREAKER",
                    "data": {
                        "containment_reason": verdict["containment_reason"],
                        "ast_primitives": verdict["ast_primitives"],
                        "latency_ms": verdict["latency_ms"],
                        "sha256_dossier": verdict["sha256_dossier"]
                    }
                }
            }

        # Approved: Forward request with execution token metadata
        if execution_handler:
            return execution_handler(request, execution_token=verdict["token"])

        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "status": "APPROVED",
                "token": verdict["token"],
                "latency_ms": verdict["latency_ms"],
                "sha256_dossier": verdict["sha256_dossier"]
            }
        }
