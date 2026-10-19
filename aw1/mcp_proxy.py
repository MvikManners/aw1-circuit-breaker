import urllib.request
import urllib.error
import datetime
import time
import os
import os
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
        except (KeyError, TypeError, IndexError, AttributeError):
            pass
    return default


def _dispatch_containment_webhook(dossier_record: dict):
    """Dispatches fail-safe incident notification upon circuit breaker containment."""
    config_file = "/home/LavetoLab/aw1-breaker/webhook_config.json"
    webhook_url = os.environ.get("AW1_WEBHOOK_URL", "")
    log_file = "/home/LavetoLab/aw1-breaker/dossiers/webhook_audit.log"
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as cf:
                cfg = json.load(cf)
                if not webhook_url:
                    webhook_url = cfg.get("webhook_url", "")
                log_file = cfg.get("log_file", log_file)
        except Exception:
            pass
    alert_payload = {
        "event": "CIRCUIT_BREAKER_CONTAINMENT",
        "severity": "CRITICAL",
        "timestamp_iso": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "dossier_hash": dossier_record.get("dossier_hash"),
        "tool_name": dossier_record.get("tool_name"),
        "actor_id": dossier_record.get("actor_id"),
        "amount_bwp": dossier_record.get("amount"),
        "containment_reason": dossier_record.get("containment_reason"),
        "remediation": f"Dual-control Ed25519 review: python3 release_dossier.py {dossier_record.get('dossier_hash', '')[:16]} <officer_id> <signature>"
    }
    # 1. Local audit append (guaranteed receipt)
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as lf:
            lf.write(json.dumps(alert_payload) + "\n")
    except Exception:
        pass
    # 2. Remote HTTP POST dispatch (if configured)
    if webhook_url and webhook_url.startswith("http"):
        try:
            data = json.dumps(alert_payload).encode("utf-8")
            req = urllib.request.Request(
                webhook_url,
                data=data,
                headers={"Content-Type": "application/json", "User-Agent": "AW1-Circuit-Breaker/1.0"}
            )
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                pass
        except Exception:
            pass

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
            sha256_dossier = (
                _extract_val(verdict, "sha256_dossier", "") or
                _extract_val(verdict, "dossier_hash", "")
            )

            # Persist immutable containment dossier to disk
            dossier_record = {
                "dossier_hash": sha256_dossier,
                "timestamp": time.time(),
                "actor_id": actor_id,
                "tool_name": tool_name,
                "amount": amount,
                "decision": str(_extract_val(verdict, "decision", "")),
                "status": status,
                "containment_reason": reason,
                "ast_primitives": _extract_val(verdict, "ast_primitives", []),
                "latency_ms": _extract_val(verdict, "latency_ms", 0.0),
                "payload": arguments
            }
            try:
                os.makedirs("/home/LavetoLab/aw1-breaker/dossiers", exist_ok=True)
                dossier_file = f"/home/LavetoLab/aw1-breaker/dossiers/{sha256_dossier[:16]}.json"
                with open(dossier_file, "w", encoding="utf-8") as f:
                    json.dump(dossier_record, f, indent=2)
            except Exception:
                pass
            _dispatch_containment_webhook(dossier_record)

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
                        "sha256_dossier": sha256_dossier
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
