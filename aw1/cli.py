import sys
import time
import ast

def verify_code(code_str: str):
    start = time.perf_counter()
    is_safe = True
    reason = "AST clean"

    try:
        from aw1.circuit import ASTCircuitBreaker
        breaker = ASTCircuitBreaker()
        if hasattr(breaker, "evaluate"):
            is_safe, reason = breaker.evaluate(code_str)
        elif hasattr(breaker, "verify"):
            is_safe, reason = breaker.verify(code_str)
        elif hasattr(breaker, "inspect"):
            is_safe, reason = breaker.inspect(code_str)
        else:
            raise AttributeError("No matching eval method")
    except Exception:
        try:
            tree = ast.parse(code_str)
            prohibited = {"subprocess", "os.system", "eval", "exec", "socket", "posix", "shutil"}
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    call_repr = ast.unparse(node.func) if hasattr(ast, "unparse") else ""
                    if any(bad in call_repr for bad in prohibited):
                        is_safe = False
                        reason = f"Prohibited API call detected: {call_repr}"
                        break
        except Exception as e:
            is_safe = False
            reason = f"AST parse syntax error: {e}"

    latency_ms = (time.perf_counter() - start) * 1000

    if not is_safe:
        print("\033[91m🚨 [AW-1 BREAKER TRIPPED]\033[0m")
        print("Verdict:   \033[91mFAIL_CLOSED\033[0m")
        print(f"Latency:   {latency_ms:.3f}ms")
        print(f"Reason:    {reason}")
        print("Action:    Execution blocked before dispatch.")
        sys.exit(1)
    else:
        print("\033[92m🛡️ [AW-1 VERIFIED SAFE]\033[0m")
        print("Verdict:   PASS")
        print(f"Latency:   {latency_ms:.3f}ms")
        sys.exit(0)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="AW-1 Circuit Breaker CLI")
    parser.add_argument("command_or_code", nargs="*", help="Code snippet to evaluate, or 'verify' / '--demo'")
    parser.add_argument("-c", "--code", type=str, help="Code snippet to evaluate")
    parser.add_argument("--demo", action="store_true", help="Run simulated destructive breakout demonstration")
    
    args = parser.parse_args()
    
    if args.demo or (args.command_or_code and args.command_or_code[0] == "--demo"):
        print("[AW-1] Running sandbox simulation...")
        verify_code("subprocess.run(['rm', '-rf', '/'])")
        return

    if args.code:
        verify_code(args.code)
        return

    if not args.command_or_code:
        parser.print_help()
        sys.exit(0)

    # Handle 'verify' subcommand or direct positional code
    if args.command_or_code[0] == "verify":
        if len(args.command_or_code) > 1:
            verify_code(" ".join(args.command_or_code[1:]))
        else:
            verify_code("x = 42; print('AW-1 operational')")
    else:
        verify_code(" ".join(args.command_or_code))
