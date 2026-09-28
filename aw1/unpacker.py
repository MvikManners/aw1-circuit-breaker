import base64
import ast
import re
from typing import List, Tuple

class ASTSymbolicUnpacker:
    """
    Decompiles polyglots, base64 strings, and eval wrappers 
    into raw execution primitives prior to tool invocation.
    """
    PAYOUT_KEYWORDS = {"transfer", "payout", "drain", "send", "withdraw", "disburse"}
    CRITICAL_TARGETS = {"hot_wallet", "core_ledger", "treasury", "vault", "reserve"}
    
    POLYGLOT_SIGNATURES = [
        "eval(", "exec(", "system(", "popen(", "subprocess", 
        "__import__", "importlib", "shutil", "posix", "pty"
    ]

    DANGEROUS_CALLS = {
        "call", "run", "check_call", "check_output", "popen",
        "system", "exec", "eval", "spawn", "execve", "execl"
    }

    def decompile(self, payload: str) -> Tuple[List[str], str]:
        normalized = payload.strip()
        
        # Check and decode base64 wrapper
        if normalized.startswith("base64:"):
            try:
                b64_content = normalized.split("base64:", 1)[1]
                decoded = base64.b64decode(b64_content).decode("utf-8", errors="ignore")
                normalized = decoded
            except Exception:
                pass

        primitives = []
        lower_payload = normalized.lower()

        # 1. Financial & Target Trajectory Detection
        if any(kw in lower_payload for kw in self.PAYOUT_KEYWORDS):
            primitives.append("[FINANCIAL_PAYOUT]")
        if any(target in lower_payload for target in self.CRITICAL_TARGETS):
            primitives.append("[HIGH_VALUE_ONE_WAY_DOOR]")

        # 2. String Signature Fast-Path Check
        detected_polyglot = any(sig in lower_payload for sig in self.POLYGLOT_SIGNATURES)

        # 3. Deep AST Traversal (if payload looks like executable code)
        if not detected_polyglot:
            try:
                tree = ast.parse(normalized)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        func_name = ""
                        if isinstance(node.func, ast.Name):
                            func_name = node.func.id
                        elif isinstance(node.func, ast.Attribute):
                            func_name = node.func.attr
                        
                        if func_name.lower() in self.DANGEROUS_CALLS:
                            detected_polyglot = True
                            break
            except Exception:
                pass

        if detected_polyglot:
            primitives.append("[CODE_EVAL_POLYGLOT]")

        return primitives, normalized
