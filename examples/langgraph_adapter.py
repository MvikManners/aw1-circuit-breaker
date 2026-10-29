"""
AW-1 Circuit Breaker: LangGraph / Autonomous Agent Pre-Execution Hook
Intercepts LLM tool calls before they hit Python runtimes or external shells.
"""

from typing import Any, Callable, Dict
import ast
import re

DANGEROUS_SHELL_PATTERNS = [r";\s*rm\s+-rf", r"\|\s*bash", r"\|\s*sh", r"/dev/tcp/"]
FORBIDDEN_CALLS = {"eval", "exec", "compile", "__import__", "subprocess.Popen", "socket.socket"}


class CircuitBreakerException(Exception):
    """Raised when an autonomous agent emits an unsafe tool execution payload."""
    pass


def guard_agent_tool_call(tool_name: str, arguments: Dict[str, Any]) -> None:
    """Pre-execution interceptor for LangGraph ToolNode or agent loops."""
    # 1. Shell argument screening
    for key, value in arguments.items():
        if isinstance(value, str):
            for pattern in DANGEROUS_SHELL_PATTERNS:
                if re.search(pattern, value):
                    raise CircuitBreakerException(
                        f"[AW-1] Shell breakout blocked in tool '{tool_name}' argument '{key}'"
                    )

    # 2. Python code AST inspection
    if "code" in arguments and isinstance(arguments["code"], str):
        try:
            tree = ast.parse(arguments["code"])
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    name = ""
                    if isinstance(node.func, ast.Name):
                        name = node.func.id
                    elif isinstance(node.func, ast.Attribute):
                        name = node.func.attr
                    if name in FORBIDDEN_CALLS:
                        raise CircuitBreakerException(
                            f"[AW-1] AST invocation trip: Forbidden call '{name}()' prevented."
                        )
        except SyntaxError as e:
            raise CircuitBreakerException(f"[AW-1] Malformed syntax rejected: {e}")


def execute_agent_action(tool_func: Callable, tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Wrapped tool execution function."""
    # Intercept first
    guard_agent_tool_call(tool_name, arguments)
    # Execute only if passed
    return tool_func(**arguments)


# --- Simulation Example ---
if __name__ == "__main__":
    def bash_tool(cmd: str):
        return f"Executed: {cmd}"

    def python_repl_tool(code: str):
        return f"Executed code: {code}"

    print("[*] Testing LangGraph Interceptor with Benign Tool Call...")
    res = execute_agent_action(bash_tool, "bash_tool", {"cmd": "ls -la /home/user"})
    print(f"    -> Status: SUCCESS ({res})")

    print("\n[*] Testing LangGraph Interceptor with Adversarial Shell Call...")
    try:
        execute_agent_action(bash_tool, "bash_tool", {"cmd": "ls /var; rm -rf /tmp/test"})
    except CircuitBreakerException as err:
        print(f"    -> Status: INTERCEPTED ({err})")

    print("\n[*] Testing LangGraph Interceptor with Rogue Python Call...")
    try:
        execute_agent_action(python_repl_tool, "python_repl", {"code": "eval('__import__(\"os\").system(\"id\")')"})
    except CircuitBreakerException as err:
        print(f"    -> Status: INTERCEPTED ({err})")
