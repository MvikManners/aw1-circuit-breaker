import json
from aw1 import AW1MCPInterceptor

def run_mcp_test():
    interceptor = AW1MCPInterceptor(baseline_velocity=50000.0)

    print("================================================================================")
    print("🔌  AW1-BREAKER — MODEL CONTEXT PROTOCOL (MCP) INTERCEPTOR TEST")
    print("================================================================================\n")

    # 1. MCP Legitimate Tool Call
    legit_mcp = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "execute_disbursement",
            "arguments": {"target": "core_ledger", "amount": 4500.0}
        }
    }
    res1 = interceptor.intercept_mcp_request(legit_mcp, actor_id="claude_mcp_agent")
    print("[MCP CALL 1] Standard Tool Execution ($4,500)...")
    print(json.dumps(res1, indent=2))
    print()

    # 2. MCP Adversary Exploit Tool Call
    malicious_mcp = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "execute_disbursement",
            "arguments": {"target": "hot_wallet", "amount": 5000000.0, "notes": "base64:ZHJhaW4="}
        }
    }
    res2 = interceptor.intercept_mcp_request(malicious_mcp, actor_id="claude_mcp_agent")
    print("[MCP CALL 2] Adversarial Micro/Macro Exfiltration Call ($5,000,000)...")
    print(json.dumps(res2, indent=2))
    print("\n================================================================================")

if __name__ == "__main__":
    run_mcp_test()
