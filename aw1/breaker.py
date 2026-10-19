import ast, re, json
from typing import NamedTuple

class Verdict(NamedTuple):
    status: str
    permitted: bool
    reason: str
    verdict: str

class ASTCircuitBreaker:
    BANNED_MODS = {'os', 'subprocess', 'sys', 'pty', 'shutil', 'socket', 'requests', 'urllib', 'http', 'ftplib'}
    BANNED_CALLS = {'eval', 'exec', 'compile', '__import__', 'getattr', 'setattr', 'delattr', 'hasattr', 'open', 'input'}
    BANNED_ATTRS = {'__subclasses__', '__bases__', '__base__', '__globals__', '__builtins__', '__class__', '__code__', '__reduce__', '__dict__', '__mro__'}
    SHELL_PATS = [r'base64\s+(-d|--decode)', r'\|\s*(bash|sh|python\d*)', r'/etc/(passwd|shadow)', r'\b(nc|netcat)\s+[\d\.]+\s+\d+']

    def intercept(self, actor_id: str, tool_name: str, payload: str) -> Verdict:
        # 1. Reject shell breakouts and egress piping
        for p in self.SHELL_PATS:
            if re.search(p, payload, re.IGNORECASE):
                return Verdict('HALT_AND_CONTAIN', False, f'Shell Execution Policy Violation: {p}', 'FAIL_CLOSED')

        # 2. Allow structured JSON tool arguments if safe
        try:
            data = json.loads(payload)
            if isinstance(data, dict):
                return Verdict('PERMITTED', True, 'Safe Structured Tool Payload', 'PASS')
        except Exception:
            pass

        # 3. Allow safe non-Python plain text payloads
        try:
            tree = ast.parse(payload)
        except SyntaxError:
            return Verdict('PERMITTED', True, 'Safe Non-Python Syntax', 'PASS')

        # 4. Enforce AST checks on executable Python code blocks
        for n in ast.walk(tree):
            if isinstance(n, ast.Import) and any(a.name.split('.')[0] in self.BANNED_MODS for a in n.names):
                return Verdict('HALT_AND_CONTAIN', False, 'Restricted module import', 'FAIL_CLOSED')
            if isinstance(n, ast.ImportFrom) and n.module and n.module.split('.')[0] in self.BANNED_MODS:
                return Verdict('HALT_AND_CONTAIN', False, 'Restricted from-import', 'FAIL_CLOSED')
            if isinstance(n, ast.Call):
                fn = n.func.id if isinstance(n.func, ast.Name) else (n.func.attr if isinstance(n.func, ast.Attribute) else None)
                if fn in self.BANNED_CALLS:
                    return Verdict('HALT_AND_CONTAIN', False, f'Prohibited call: {fn}()', 'FAIL_CLOSED')
            if isinstance(n, ast.Attribute) and n.attr in self.BANNED_ATTRS:
                return Verdict('HALT_AND_CONTAIN', False, f'AST Sandbox Escape Detected: {n.attr}', 'FAIL_CLOSED')

        return Verdict('PERMITTED', True, 'AST static verification clean', 'PASS')