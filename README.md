# AW-1 Breaker

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9+-brightgreen.svg)]()
[![Telemetry SLA](https://img.shields.io/badge/Fast--Path%20SLA-%3C005ms-success)]()

**Deterministic, sub-millisecond execution circuit breaker for autonomous AI agent tool-calls.**

Standard LLM guardrails (RLHF, system prompt boundaries) operate *in-band*: models evaluate their own compliance. When autonomous agents are granted tool-calling access to system shells, databases, or financial disbursement rails, adversarial injections or goal drift can bypass prompt restrictions via Base64 obfuscation, polyglot payloads, or velocity micro-drains.

`aw1-breaker` enforces an **out-of-band execution interlock** between the agent reasoning node and downstream execution sockets.

---

## Installation

```bash
pip install aw1-breaker
```

---

## Quickstart

```python
from aw1 import ExecutionBreaker

breaker = ExecutionBreaker(baseline_velocity=50000.0)
result = breaker.intercept(
    actor_id="agent_treasury_01",
    tool_name="disburse_funds",
    payload='{"target": "core_ledger", "action": "payout"}',
    amount=12000.0
)
print(result)
```

---

## License
MIT License. Designed and maintained by Laveto Labs.
