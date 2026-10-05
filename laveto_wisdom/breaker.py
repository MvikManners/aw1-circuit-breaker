import ast
import hashlib
from laveto_wisdom.canary import SyntheticCanary
from laveto_wisdom.quorum import QuorumEngine
from laveto_wisdom.statutory import StatutoryLensEngine
from laveto_wisdom.synthesizer import RuleSynthesizer
from laveto_wisdom.tee import TEEAttestationEngine

class SecurityTripwireException(Exception):
    pass

class ExecutionBreaker:
    """
    AW-1 Deterministic Execution Guard:
    Tier 1: AST Static Analysis, Dynamic Synthesized Rules, & Canary Honeypot
    Tier 2: Statutory Data Sovereignty & Fiduciary Trust Lenses
    Tier 3: Multi-Agent Quorum Consensus
    Tier 4: Hardware-Rooted TEE Enclave Attestation
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

        # 1. Base Static Prohibitions
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

        # 2. Dynamic Synthesized AST Invariant Evaluation
        rules = RuleSynthesizer.load_active_rules()
        for node in ast.walk(tree):
            for r in rules:
                if r['target_node'] == 'Call' and isinstance(node, ast.Call):
                    if "getattr" in r['predicate'] and isinstance(node.func, ast.Name) and node.func.id == 'getattr':
                        if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                            if node.args[1].value in r['predicate']:
                                return f"SYNTHESIZED_INVARIANT_TRIP_{r['pattern']}"

        # 3. Autonomous Evasion Pattern Analysis & Dynamic Synthesis
        synthesized_id = RuleSynthesizer.analyze_and_synthesize(code_str)
        if synthesized_id:
            return f"AUTONOMOUS_SYNTHESIZED_INTERCEPTION_{synthesized_id}"

        return None

    def execute_tool(self, tool_name: str, payload: str, session_id: str = "agent-session-001",
                     agent_id: str = "agent_planner", cost_bwp: float = 0.0,
                     attestations: list = None, quorum_threshold: int = 2):
        
        payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()

        # Tier 1: AST Structural Inspection & Canary Tripwire
        threat_vector = self._inspect_ast(payload)
        if threat_vector:
            if self.enable_canary:
                trap = SyntheticCanary.synthesize_decoy(
                    tool_name=tool_name,
                    payload=payload,
                    threat_vector=threat_vector,
                    session_id=session_id
                )
                tee_token = TEEAttestationEngine.issue_attestation(trap["dossier_id"], session_id)
                return {
                    "execution_status": "SUCCESS",
                    "output": trap["synthetic_output"],
                    "security_audit": {
                        "circuit_breaker": "TRIPPED_CANARY",
                        "threat_vector": threat_vector,
                        "dossier_id": trap["dossier_id"],
                        "tee_attestation": tee_token
                    }
                }
            else:
                raise SecurityTripwireException(f"AST Circuit Breaker Trip: {threat_vector}")

        # Tier 2: Dynamic Statutory & Fiduciary Lenses
        statutory_clear, reason, decision = StatutoryLensEngine.audit_and_contain(
            agent_id=agent_id,
            tool_name=tool_name,
            payload=payload,
            estimated_cost_bwp=cost_bwp
        )
        if not statutory_clear:
            dossier_hash = hashlib.sha256(f"{payload_hash}:{decision}:{reason}".encode('utf-8')).hexdigest()
            tee_token = TEEAttestationEngine.issue_attestation(dossier_hash, session_id)
            return {
                "execution_status": "BLOCKED",
                "output": f"Circuit breaker tripped by Statutory Lens: {reason}",
                "security_audit": {
                    "circuit_breaker": decision,
                    "reason": reason,
                    "tee_attestation": tee_token
                }
            }

        # Tier 3: Cryptographic Multi-Agent Quorum Consensus Check
        if tool_name in QuorumEngine.CRITICAL_TOOLS:
            is_valid, msg, quorum_id = QuorumEngine.verify_attestations(
                tool_name=tool_name,
                payload=payload,
                attestations=attestations or [],
                threshold=quorum_threshold
            )
            if not is_valid:
                dossier_hash = hashlib.sha256(f"{payload_hash}:QUORUM_REJECTED:{msg}".encode('utf-8')).hexdigest()
                tee_token = TEEAttestationEngine.issue_attestation(dossier_hash, session_id)
                return {
                    "execution_status": "BLOCKED",
                    "output": f"Circuit breaker halted '{tool_name}': {msg}",
                    "security_audit": {
                        "circuit_breaker": "QUORUM_REJECTED",
                        "reason": msg,
                        "tee_attestation": tee_token
                    }
                }
            
            tee_token = TEEAttestationEngine.issue_attestation(quorum_id, session_id)
            return {
                "execution_status": "SUCCESS",
                "output": f"Critical tool '{tool_name}' authorized under multi-agent quorum consensus.",
                "security_audit": {
                    "circuit_breaker": "QUORUM_ATTESTED",
                    "quorum_id": quorum_id,
                    "threshold_met": quorum_threshold,
                    "tee_attestation": tee_token
                }
            }

        # Tier 4: Standard Permitted Path with TEE Attestation
        clean_dossier = hashlib.sha256(f"{payload_hash}:PERMITTED".encode('utf-8')).hexdigest()
        tee_token = TEEAttestationEngine.issue_attestation(clean_dossier, session_id)
        return {
            "execution_status": "SUCCESS",
            "output": f"Legitimate tool '{tool_name}' executed safely.",
            "security_audit": {
                "circuit_breaker": "PERMITTED",
                "tee_attestation": tee_token
            }
        }
