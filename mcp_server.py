"""
AW-1 Execution Guard: Deterministic AST Circuit Breaker MCP Server
"""
import ast
import json
from typing import Any, Dict, List
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP(
    name="aw1-circuit-breaker",
    instructions="Deterministic AST deconstruction and runtime circuit breaker preventing rogue shell escapes, dynamic eval(), and covert lateral socket egress."
)

BLOCKED_CALLS = {
    "eval", "exec", "compile", "__import__", "breakpoint"
}

BLOCKED_MODULES = {
    "os", "subprocess", "socket", "pty", "posix", "shutil", "commands"
}

BLOCKED_ATTRIBUTES = {
    "system", "popen", "spawn", "execv", "execl", "connect", "bind", "rmtree"
}


class CircuitBreakerVisitor(ast.NodeVisitor):
    def __init__(self):
        self.violations: List[str] = []
        self.analyzed_nodes: int = 0

    def visit(self, node: ast.AST):
        self.analyzed_nodes += 1
        super().visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in BLOCKED_CALLS:
            self.violations.append(
                f"Blocked execution of banned builtin: '{node.func.id}()' at line {node.lineno}"
            )
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in BLOCKED_ATTRIBUTES:
                if isinstance(node.func.value, ast.Name) and node.func.value.id in BLOCKED_MODULES:
                    self.violations.append(
                        f"Blocked dangerous module invocation: '{node.func.value.id}.{node.func.attr}()' at line {node.lineno}"
                    )
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            base_module = alias.name.split(".")[0]
            if base_module in BLOCKED_MODULES:
                self.violations.append(
                    f"Blocked unauthorized module import: '{alias.name}' at line {node.lineno}"
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            base_module = node.module.split(".")[0]
            if base_module in BLOCKED_MODULES:
                self.violations.append(
                    f"Blocked unauthorized module import: '{node.module}' at line {node.lineno}"
                )
        self.generic_visit(node)


@mcp.tool()
def inspect_python_code(code: str) -> str:
    """
    Deconstructs and analyzes Python code AST for unsafe constructs,
    shell injection, dynamic evaluation, and socket egress.
    """
    try:
        parsed_tree = ast.parse(code)
    except SyntaxError as err:
        return json.dumps({
            "status": "error",
            "safe": False,
            "message": f"Syntax parsing failure: {err}"
        }, indent=2)

    visitor = CircuitBreakerVisitor()
    visitor.visit(parsed_tree)

    is_safe = len(visitor.violations) == 0
    return json.dumps({
        "status": "success",
        "safe": is_safe,
        "nodes_evaluated": visitor.analyzed_nodes,
        "violations": visitor.violations,
        "recommendation": "ALLOW" if is_safe else "CIRCUIT_BREAKER_TRIPPED"
    }, indent=2)


@mcp.tool()
def inspect_tool_arguments(tool_name: str, arguments_json: str) -> str:
    """
    Validates arguments passed to external tools for risky shell patterns,
    eval triggers, or socket connections.
    """
    try:
        args = json.loads(arguments_json)
    except Exception:
        return json.dumps({
            "status": "error",
            "safe": False,
            "message": "Malformed JSON arguments."
        }, indent=2)

    flagged_patterns = []
    serialized = str(args)

    for keyword in ["eval(", "exec(", "sh -c", "bash -c", "/bin/sh", "nc -e", "socket.socket"]:
        if keyword in serialized:
            flagged_patterns.append(f"Detected suspicious token: '{keyword}'")

    is_safe = len(flagged_patterns) == 0
    return json.dumps({
        "status": "success",
        "tool": tool_name,
        "safe": is_safe,
        "flagged_tokens": flagged_patterns,
        "recommendation": "ALLOW" if is_safe else "REJECT_TOOL_CALL"
    }, indent=2)


@mcp.tool()
def get_containment_status() -> str:
    """Returns the current state of zero-trust AST containment rules."""
    return json.dumps({
        "status": "ACTIVE",
        "engine": "AW-1 Deterministic AST Breaker",
        "blocked_builtins": sorted(list(BLOCKED_CALLS)),
        "blocked_modules": sorted(list(BLOCKED_MODULES)),
        "mode": "Zero-Trust Enforcement"
    }, indent=2)


if __name__ == "__main__":
    mcp.run()
def main():
    mcp.run()

if __name__ == "__main__":
    main()
