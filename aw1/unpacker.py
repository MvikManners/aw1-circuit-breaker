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
    NETWORK_SIGNATURES = [
        "socket", "connect(", "http", "urllib", "requests", "httpx", "aiohttp"
    ]
    DANGEROUS_CALLS = {
        "call", "run", "check_call", "check_output", "popen",
        "system", "exec", "eval", "spawn", "execve", "execl"
    }
    NETWORK_CALLS = {"connect", "get", "post", "send", "sendall", "sendto", "request"}
    KERNEL_TARGET_PREFIXES = ("/proc", "/sys", "/etc", "/dev", "/boot", "/root")
    SHELL_CALLS = {"system", "popen", "spawn", "execve", "execl"}

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
        detected_network = any(sig in lower_payload for sig in self.NETWORK_SIGNATURES)
        detected_kernel_write = False
        detected_shell = any(sig in lower_payload for sig in ("subprocess", "popen(", "system(", "pty"))
        
        # Fast-path check for sensitive kernel/sysfs write targets
        if any(tgt in lower_payload for tgt in self.KERNEL_TARGET_PREFIXES):
            if any(w in lower_payload for w in ("'w'", '"w"', "'a'", '"a"', "'wb'", '"wb"', "'w+'", '"w+"', ".write", "truncate")):
                detected_kernel_write = True
        
        # 3. Deep AST Traversal (if payload looks like executable code)
        try:
            tree = ast.parse(normalized)
            for node in ast.walk(tree):
                # Inspect imports for network and execution libraries
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    names = [n.name.lower() for n in getattr(node, "names", [])]
                    mod = getattr(node, "module", "") or ""
                    all_mods = names + [mod.lower()]
                    if any("socket" in m or "urllib" in m or "http" in m for m in all_mods):
                        detected_network = True
                    if any(m in ("subprocess", "os", "sys", "shutil") for m in all_mods):
                        detected_polyglot = True
                    if any(m in ("subprocess", "pty") for m in all_mods):
                        detected_shell = True

                # Inspect function calls
                if isinstance(node, ast.Call):
                    func_name = ""
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                    elif isinstance(node.func, ast.Attribute):
                        func_name = node.func.attr
                    
                    fn_lower = func_name.lower()
                    if fn_lower in self.DANGEROUS_CALLS:
                        detected_polyglot = True
                    if fn_lower in self.SHELL_CALLS:
                        detected_shell = True
                    if fn_lower in self.NETWORK_CALLS:
                        detected_network = True
                        
                    # Kernel/System file write detection via open()
                    if fn_lower == "open" and node.args:
                        path_val = None
                        arg0 = node.args[0]
                        if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                            path_val = arg0.value
                        elif hasattr(ast, "Str") and isinstance(arg0, getattr(ast, "Str")):
                            path_val = arg0.s
                            
                        mode_val = ""
                        if len(node.args) > 1:
                            arg1 = node.args[1]
                            if isinstance(arg1, ast.Constant) and isinstance(arg1.value, str):
                                mode_val = arg1.value
                            elif hasattr(ast, "Str") and isinstance(arg1, getattr(ast, "Str")):
                                mode_val = arg1.s
                        for kw in node.keywords:
                            if kw.arg == "mode":
                                if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                                    mode_val = kw.value.value
                                elif hasattr(ast, "Str") and isinstance(kw.value, getattr(ast, "Str")):
                                    mode_val = kw.value.s
                                    
                        if path_val:
                            p_low = path_val.lower()
                            if any(p_low.startswith(p) for p in self.KERNEL_TARGET_PREFIXES):
                                if any(m in mode_val for m in ("w", "a", "x", "+")) or not mode_val:
                                    detected_kernel_write = True
        except Exception:
            pass

        if detected_polyglot:
            primitives.append("[CODE_EVAL_POLYGLOT]")
        if detected_shell and "[SYSTEM_SHELL_EXEC]" not in primitives:
            primitives.append("[SYSTEM_SHELL_EXEC]")
        if detected_kernel_write and "[KERNEL_WRITE]" not in primitives:
            primitives.append("[KERNEL_WRITE]")
        if detected_network:
            primitives.append("[NETWORK_EGRESS]")
            
        return primitives, normalized
