import ast, base64, re
from typing import NamedTuple, Optional

class Verdict(NamedTuple):
    status: str
    permitted: bool
    reason: str
    verdict: str

class ASTCircuitBreaker:
    BANNED_MODS = {"os", "subprocess", "sys", "pty", "shutil", "socket", "requests", "urllib", "http", "ftplib", "telnetlib", "posix"}
    BANNED_CALLS = {"eval", "exec", "compile", "__import__", "getattr", "setattr", "delattr", "hasattr", "open", "input"}
    BANNED_ATTRS = {"__subclasses__", "__bases__", "__base__", "__globals__", "__builtins__", "__class__", "__code__", "__reduce__", "__dict__", "__mro__"}
    SHELL_PATS = [r"base64\s+(-d|--decode)", r"\|\s*(bash|sh|python\d*)", r"/etc/(passwd|shadow)", r"(nc|netcat)\s+[\d\.]+\s+\d+"]

    def _resolve(self, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str): return node.value
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            l, r = self._resolve(node.left), self._resolve(node.right)
            if l and r: return l + r
        return None

    def intercept(self, actor_id: str, tool_name: str, payload: str) -> Verdict:
        # Base64 pre-scan
        for m in re.findall(r"[A-Za-z0-9+/]{8,}={0,2}", payload):
            try:
                dec = base64.b64decode(m + "=" * ((4 - len(m) % 4) % 4)).decode("utf-8", errors="ignore").lower()
                if any(k in dec for k in ["os.", "system", "sh", "pty", "cat ", "drop ", "subclasses", "eval", "exec", "id"]):
                    return Verdict("HALT_AND_CONTAIN", False, "Obfuscation Intercept: Encoded base64 payload hides dangerous primitives", "FAIL_CLOSED")
            except Exception: pass

        # Shell chaining and pipe detection
        for p in self.SHELL_PATS:
            if re.search(p, payload, re.IGNORECASE):
                return Verdict("HALT_AND_CONTAIN", False, f"Shell Execution Policy Violation: {p}", "FAIL_CLOSED")

        try: tree = ast.parse(payload)
        except SyntaxError:
            return Verdict("PERMITTED", True, "Safe Non-Python Syntax", "PASS")

        # Recursive AST Walk
        for n in ast.walk(tree):
            if isinstance(n, ast.Import) and any(a.name.split(".")[0] in self.BANNED_MODS for a in n.names):
                return Verdict("HALT_AND_CONTAIN", False, "Restricted module import", "FAIL_CLOSED")
            if isinstance(n, ast.ImportFrom) and n.module and n.module.split(".")[0] in self.BANNED_MODS:
                return Verdict("HALT_AND_CONTAIN", False, "Restricted from-import", "FAIL_CLOSED")
            if isinstance(n, ast.Call):
                fn = n.func.id if isinstance(n.func, ast.Name) else (n.func.attr if isinstance(n.func, ast.Attribute) else None)
                if fn in self.BANNED_CALLS:
                    return Verdict("HALT_AND_CONTAIN", False, f"Prohibited reflection/eval call '{fn}()'", "FAIL_CLOSED")
                if fn == "getattr" and len(n.args) >= 2 and self._resolve(n.args[1]) in ("system", "popen", "spawn", "exec", "eval"):
                    return Verdict("HALT_AND_CONTAIN", False, "Polymorphic getattr prohibited", "FAIL_CLOSED")
            if isinstance(n, ast.Attribute) and n.attr in self.BANNED_ATTRS:
                return Verdict("HALT_AND_CONTAIN", False, f"AST Sandbox Escape Detected: '{n.attr}'", "FAIL_CLOSED")

        return Verdict("PERMITTED", True, "AST static verification clean", "PASS")
