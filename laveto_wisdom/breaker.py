import ast
from laveto_wisdom.canary import SyntheticCanary
from laveto_wisdom.quorum import QuorumEngine

class SecurityTripwireException(Exception):
    pass

class ExecutionBreaker:
    """
    AW-1 Deterministic AST Circuit Breaker with Canary Honeypot & Multi-Agent Quorum Verification.
    """
    FORBIDDEN_CALLS = {'eval', 'exec', '__import__', 'compile'}
    FORBIDDEN_MODULES = {'os', 'sys', 'subprocess', 'shutil', 'socket', 'pty'}

    def __init__(self, license_key: str, enable_canary: bool = True):
        self.license_key = license_key
        self.enable_canary = enable_canary

    def _inspect_ast(self, code_str: str):
        try:
            tree = ast.parse(code_str)
        except SyntaxError:
            return "NON_PYTHON_POLYGLOT_PAYLOAD"

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in self.FORBIDDEN_CALLS:
                    return f"FORBIDDEN_CALL_{node.func.id.upper()}"
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.FORBIDDEN_MODULES:
                        return f"FORBIDDEN_IMPORT_{alias.name.upper()}"
            elif isinstance(node, ast.ImportFrom):
                if node.module in self.FORBIDDEN_MODULES:
                    return f"FORBIDDEN_IMPORT_{node.module.upper()}"
        return None

    def execute_tool(self, tool_name: str, payload: str, session_id: str = "agent-session-001", attestations: list = None, quorum_threshold: int = 2):
        """
        Validates AST safety, diverts attacks into Canary, and enforces cryptographic
        multi-agent quorum consensus for sensitive actions.
        """
        # 1. AST Structural Inspection
        threat_vector = self._inspect_ast(payload)
        if threat_vector:
            if self.enable_canary:
                trap = SyntheticCanary.synthesize_decoy(
                    tool_name=tool_name,
                    payload=payload,
                    threat_vector=threat_vector,
                    session_id=session_id
                )
                return {
                    "execution_status": "SUCCESS",
                    "output": trap["synthetic_output"],
                    "security_audit": {
                        "circuit_breaker": "TRIPPED_CANARY",
                        "dossier_id": trap["dossier_id"]
                    }
                }
            else:
                raise SecurityTripwireException(f"AST Circuit Breaker Trip: {threat_vector}")

        # 2. Multi-Agent Quorum Consensus Check
        if tool_name in QuorumEngine.CRITICAL_TOOLS:
            is_valid, msg, quorum_id = QuorumEngine.verify_attestations(
                tool_name=tool_name,
                payload=payload,
                attestations=attestations or [],
                threshold=quorum_threshold
            )
            if not is_valid:
                return {
                    "execution_status": "BLOCKED",
                    "output": f"Circuit breaker halted '{tool_name}': {msg}",
                    "security_audit": {
                        "circuit_breaker": "QUORUM_REJECTED",
                        "reason": msg
                    }
                }
            
            return {
                "execution_status": "SUCCESS",
                "output": f"Critical tool '{tool_name}' authorized under multi-agent quorum consensus.",
                "security_audit": {
                    "circuit_breaker": "QUORUM_ATTESTED",
                    "quorum_id": quorum_id,
                    "threshold_met": quorum_threshold
                }
            }

        # 3. Standard Permitted Path
        return {
            "execution_status": "SUCCESS",
            "output": f"Legitimate tool '{tool_name}' executed safely.",
            "security_audit": {
                "circuit_breaker": "PERMITTED"
            }
        }
