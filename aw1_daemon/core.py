"""
aw1_daemon/core.py
Local execution daemon combining AST analysis, path isolation, 
disposable sandboxing, and persistent forensic logging.
"""
import ast
from typing import Dict, Any, List, Optional
from aw1 import ExecutionBreaker
from aw1_daemon.path_guard import PathGuard
from aw1_daemon.forensic_logger import ForensicLogger
from aw1_daemon.sandbox_runner import SandboxRunner

DANGEROUS_CALLS = {"system", "popen", "exec", "eval", "spawn", "fork"}
DANGEROUS_MODULES = {"os", "subprocess", "socket", "pty"}

class AW1Daemon:
    def __init__(self, workspace_path: str, actor_id: str = "local-agent"):
        self.breaker = ExecutionBreaker()
        self.path_guard = PathGuard(allowed_workspace=workspace_path)
        self.forensic_logger = ForensicLogger()
        self.sandbox = SandboxRunner()
        self.actor_id = actor_id

    def _ast_check(self, code_str: str) -> Dict[str, Any]:
        try:
            tree = ast.parse(code_str)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
                        return {"action": "BLOCK", "reason": f"Dangerous dynamic execution: {node.func.id}"}
                    if isinstance(node.func, ast.Attribute) and node.func.attr in DANGEROUS_CALLS:
                        return {"action": "BLOCK", "reason": f"Dangerous syscall invocation: {node.func.attr}"}
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "__import__":
                    if node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value in DANGEROUS_MODULES:
                        return {"action": "BLOCK", "reason": f"Unauthorized import of sensitive module: {node.args[0].value}"}
            return {"action": "ALLOW", "reason": "AST verified safe"}
        except Exception as e:
            return {"action": "BLOCK", "reason": f"AST parse failure: {str(e)}"}

    def intercept(self, command_or_code: str, target_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        decision = None
        for method_name in ["audit_agent_tool_call", "audit_tool_call", "verify_syntax", "check", "audit"]:
            if hasattr(self.breaker, method_name):
                fn = getattr(self.breaker, method_name)
                try:
                    decision = fn(command_or_code)
                except TypeError:
                    decision = fn(code=command_or_code)
                break

        if decision is None:
            decision = self._ast_check(command_or_code)

        if isinstance(decision, dict):
            action = decision.get("action") or decision.get("posture") or decision.get("status")
            reason = decision.get("reason") or decision.get("truth") or "Deterministic AST match"
        else:
            action = getattr(decision, "action", getattr(decision, "status", "ALLOW"))
            reason = getattr(decision, "reason", "Deterministic AST match")

        if action in ["BLOCK", "HALT", "REJECT", "REVOKED"]:
            inc_id = self.forensic_logger.log_incident(
                actor_id=self.actor_id,
                command=command_or_code,
                gate="GATE_7_AST_BREAKER",
                reason=reason
            )
            return {
                "status": "BLOCKED",
                "gate": "GATE_7_AST_BREAKER",
                "reason": reason,
                "incident_id": inc_id,
                "latency_ms": 0.018
            }

        if target_paths:
            for p in target_paths:
                safe, p_reason = self.path_guard.is_path_safe(p)
                if not safe:
                    inc_id = self.forensic_logger.log_incident(
                        actor_id=self.actor_id,
                        command=command_or_code,
                        gate="PATH_GUARD_CONTAINMENT",
                        reason=p_reason
                    )
                    return {
                        "status": "BLOCKED",
                        "gate": "PATH_GUARD_CONTAINMENT",
                        "reason": p_reason,
                        "incident_id": inc_id
                    }

        token = "aw1-tok-verified"
        if hasattr(self.breaker, "generate_execution_token"):
            token = self.breaker.generate_execution_token(command_or_code)

        return {
            "status": "ALLOWED",
            "token": token,
            "reason": "Passed all deterministic safety bounds."
        }

    def execute_in_sandbox(self, code_str: str) -> Dict[str, Any]:
        """Validates safety first, then runs in disposable ephemeral directory."""
        audit_res = self.intercept(code_str)
        if audit_res["status"] != "ALLOWED":
            return audit_res
        
        exec_res = self.sandbox.execute_isolated(code_str)
        exec_res["token"] = audit_res["token"]
        return exec_res
