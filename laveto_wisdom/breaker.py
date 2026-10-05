import ast
from laveto_wisdom.canary import SyntheticCanary

class SecurityTripwireException(Exception):
    pass

class ExecutionBreaker:
    """
    AW-1 Deterministic AST Circuit Breaker with Synthetic Canary Integration.
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
            # Polyglot shell or non-Python code passed as string
            return "NON_PYTHON_POLYGLOT_PAYLOAD"

        for node in ast.walk(tree):
            # Check forbidden function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in self.FORBIDDEN_CALLS:
                    return f"FORBIDDEN_CALL_{node.func.id.upper()}"
            # Check unauthorized module imports
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.FORBIDDEN_MODULES:
                        return f"FORBIDDEN_IMPORT_{alias.name.upper()}"
            elif isinstance(node, ast.ImportFrom):
                if node.module in self.FORBIDDEN_MODULES:
                    return f"FORBIDDEN_IMPORT_{node.module.upper()}"
        return None

    def execute_tool(self, tool_name: str, payload: str, session_id: str = "agent-session-001"):
        """
        Intercepts tool call: permits safe execution, or traps adversary in canary.
        """
        threat_vector = self._inspect_ast(payload)

        # Trap detected attacks
        if threat_vector:
            if self.enable_canary:
                trap = SyntheticCanary.synthesize_decoy(
                    tool_name=tool_name,
                    payload=payload,
                    threat_vector=threat_vector,
                    session_id=session_id
                )
                return {
                    "execution_status": "SUCCESS", # Deceptive success mask to fool the attacker
                    "output": trap["synthetic_output"],
                    "security_audit": {
                        "circuit_breaker": "TRIPPED_CANARY",
                        "dossier_id": trap["dossier_id"]
                    }
                }
            else:
                raise SecurityTripwireException(f"AST Circuit Breaker Trip: {threat_vector}")

        # Authorized safe execution path
        return {
            "execution_status": "SUCCESS",
            "output": f"Legitimate tool '{tool_name}' executed safely.",
            "security_audit": {
                "circuit_breaker": "PERMITTED"
            }
        }
