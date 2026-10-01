import subprocess
import json

class AW1Client:
    def __init__(self):
        self.proc = subprocess.Popen(
            ["/home/LavetoLab/lvt_backend/venv/bin/python3", "/home/LavetoLab/aw1-breaker/scripts/aw1_mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.req_id = 1

    def send(self, method, params=None):
        payload = {
            "jsonrpc": "2.0",
            "id": self.req_id,
            "method": method,
            "params": params or {}
        }
        self.req_id += 1
        self.proc.stdin.write(json.dumps(payload) + "\n")
        self.proc.stdin.flush()
        return json.loads(self.proc.stdout.readline())

    def close(self):
        self.proc.terminate()

# Test usage:
client = AW1Client()

# 1. Discover available tools
print("Discovered tools:", client.send("tools/list")["result"]["tools"])

# 2. Audit an agent tool payload before execution
result = client.send("tools/call", {
    "name": "audit_agent_tool_call",
    "arguments": {
        "target_tool": "system_exec",
        "arguments": {"command": "import os; os.system('cat /etc/passwd')"}
    }
})
print("\nBreaker Response:\n", result["result"]["content"][0]["text"])

client.close()