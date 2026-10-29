"""
AW-1 Native Model Context Protocol (MCP) Execution Guard Server
Deterministic out-of-band AST deconstruction and tool-call circuit breaker.
Compliant with Model Context Protocol (JSON-RPC 2.0 stdio transport).
"""

import sys
import json
import ast
import hashlib
import time

def evaluate_ast_safety(payload_code: str) -> dict:
    """Sub-millisecond Layer 0 AST deconstruction."""
    try:
        tree = ast.parse(payload_code)
        for node in ast.walk(tree):
            # Block dynamic code evaluation & shell escapes
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ['eval', 'exec', '__import__', 'compile']:
                    return {"verdict": "HALT", "reason": f"Disallowed dynamic execution primitive: {node.func.id}"}
                if isinstance(node.func, ast.Attribute) and node.func.attr in ['system', 'popen', 'spawn', 'execve']:
                    return {"verdict": "HALT", "reason": f"Unauthorized OS sub-process escape attempt: {node.func.attr}"}
            # Block unauthorized network socket bindings
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ['socket', 'pty', 'subprocess']:
                        return {"verdict": "HALT", "reason": f"Unauthorized lateral network/socket import: {alias.name}"}
        return {"verdict": "PERMITTED", "reason": "AST invariants verified"}
    except Exception as e:
        return {"verdict": "HALT", "reason": f"Unparseable payload / syntax violation: {str(e)}"}

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {"name": "aw1-runtime-guard", "version": "1.0.0"},
                        "capabilities": {"tools": {}}
                    }
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": [
                            {
                                "name": "aw1_verify_tool_call",
                                "description": "Deterministic AST deconstruction and runtime circuit-breaker gate for agent tool invocations.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "tool_name": {"type": "string"},
                                        "payload": {"type": "string"},
                                        "agent_id": {"type": "string"}
                                    },
                                    "required": ["tool_name", "payload"]
                                }
                            }
                        ]
                    }
                }
            elif method == "tools/call":
                t_name = params.get("name")
                args = params.get("arguments", {})
                if t_name == "aw1_verify_tool_call":
                    payload = args.get("payload", "")
                    audit = evaluate_ast_safety(payload)
                    audit_hash = hashlib.sha256(f"{payload}{time.time()}".encode()).hexdigest()
                    resp = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps({
                                        "status": "SUCCESS" if audit["verdict"] == "PERMITTED" else "HALTED",
                                        "verdict": audit["verdict"],
                                        "reason": audit["reason"],
                                        "dossier_sha256": audit_hash
                                    })
                                }
                            ]
                        }
                    }
                else:
                    resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}
            else:
                resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"AW-1 MCP Error: {e}\n")

if __name__ == "__main__":
    main()
