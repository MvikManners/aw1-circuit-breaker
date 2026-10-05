import sys
import json
from laveto_wisdom.breaker import ExecutionBreaker
from laveto_wisdom.tee import TEEAttestationEngine

class AW1MCPServer:
    """
    Standard Model Context Protocol (MCP) stdio Server.
    Enables Claude Desktop, Cursor, and Agent Swarms to govern tool calls through AW-1.
    """
    def __init__(self, license_key: str = "AW1-DEFAULT-KEY"):
        self.breaker = ExecutionBreaker(license_key=license_key, enable_canary=True)

    def handle_request(self, request: dict) -> dict:
        method = request.get("method")
        msg_id = request.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "aw1-sovereign-circuit-breaker",
                        "version": "2.0.0"
                    }
                }
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": [
                        {
                            "name": "aw1_execute_protected_tool",
                            "description": "Executes a tool call gated by the 5-Tier AW-1 Sovereign Circuit Breaker (AST Canary, Statutory Lens, Quorum, TEE Seal).",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "tool_name": {"type": "string"},
                                    "payload": {"type": "string"},
                                    "agent_id": {"type": "string", "default": "agent_planner"},
                                    "cost_bwp": {"type": "number", "default": 0.0}
                                },
                                "required": ["tool_name", "payload"]
                            }
                        },
                        {
                            "name": "aw1_verify_tee_attestation",
                            "description": "Verifies a cryptographic TEE attestation ID against immutable ledger records.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "attestation_id": {"type": "string"}
                                },
                                "required": ["attestation_id"]
                            }
                        }
                    ]
                }
            }

        elif method == "tools/call":
            params = request.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})

            if name == "aw1_execute_protected_tool":
                res = self.breaker.execute_tool(
                    tool_name=args.get("tool_name", ""),
                    payload=args.get("payload", ""),
                    agent_id=args.get("agent_id", "agent_planner"),
                    cost_bwp=args.get("cost_bwp", 0.0)
                )
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(res, indent=2)}]
                    }
                }

            elif name == "aw1_verify_tee_attestation":
                att_id = args.get("attestation_id", "")
                is_valid = TEEAttestationEngine.verify_attestation(att_id)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": f"Attestation {att_id}: {'VALID' if is_valid else 'INVALID'}"}]
                    }
                }

        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Method '{method}' not found."}
        }

    def serve_forever(self):
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                resp = self.handle_request(req)
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
            except Exception as e:
                err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()

if __name__ == "__main__":
    server = AW1MCPServer()
    server.serve_forever()
