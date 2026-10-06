# AW-1 Sovereign Runtime Guard & MCP Execution Breaker

[![MCP Compliant](https://img.shields.io/badge/MCP-2024--11--05-blue)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Latency](https://img.shields.io/badge/AST%20Gate-%3C0.2ms-brightgreen)](https://p20.laveto.net/wisdom/api/telemetry)

AW-1 is a deterministic out-of-band execution circuit breaker and Layer 0 Abstract Syntax Tree (AST) deconstruction guard for autonomous AI agents and tool invocations.

Designed to prevent execution escapes, covert lateral channels, and unconstrained API velocity in multi-agent swarms.

---

## ⚡ Quickstart with Model Context Protocol (MCP)

AW-1 includes a zero-dependency native MCP server communicating over standard `stdio` JSON-RPC 2.0.

### 1. Add to Claude Desktop
Add this to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "aw1-guard": {
      "command": "python3",
      "args": ["-m", "laveto_wisdom.mcp_server"]
    }
  }
}
```

### 2. Add to Cursor IDE
Add to `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "aw1-guard": {
      "command": "python3",
      "args": ["-m", "laveto_wisdom.mcp_server"]
    }
  }
}
```

---

## 🛡️ Architecture & Threat Containment

| Defense Tier | Mechanism | Target Vector |
| :--- | :--- | :--- |
| **Tier 1: AST Canary** | Sub-millisecond AST parser (`<0.2ms`) | Blocks `eval`, `exec`, `system`, and shell escapes before kernel dispatch |
| **Tier 2: Network Interlock** | Dynamic import containment | Prevents unauthorized `socket` and `subprocess` imports |
| **Tier 3: Swarm Quorum** | 2-of-N HMAC cryptographic gates | Mitigates emergent multi-agent collusion and covert relays |
| **Tier 5: Hardware TEE** | Enclave PCR0 measurement logs | Generates tamper-proof SHA-256 Decision Assurance Dossiers |

---

## 💻 Standalone Python Usage

```python
from laveto_wisdom import ExecutionBreaker

breaker = ExecutionBreaker(enable_canary=True)
result = breaker.execute_tool(
    tool_name="shell_runner",
    payload="cat /etc/passwd"
)

# Output: {'execution_status': 'HALTED', 'reason': 'Unauthorized system access attempt'}
```

---

## 🔌 Universal Middleware: `@protect_tool` & LangChain

```python
from laveto_wisdom.middleware import protect_tool, AW1CallbackHandler

# Protect any Python function or agent tool
@protect_tool(max_velocity_bwp=2000.0)
def disburse_funds(recipient_id: str, amount_bwp: float):
    return {"disbursed": amount_bwp, "status": "committed"}

# Attach directly to LangChain agents
agent = initialize_agent(
    tools=[disburse_funds],
    llm=llm,
    callbacks=[AW1CallbackHandler()]
)
```

---

## 📖 Specifications & Telemetry
- **Interactive Documentation**: https://p20.laveto.net/wisdom/docs
- **Live Verification Telemetry**: https://p20.laveto.net/wisdom/api/telemetry
