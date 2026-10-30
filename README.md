<!-- hol-install-block:v2 slug=mvikmanners/aw1-circuit-breaker -->
Install with [HOL Guard](https://hol.org/guard/docs/plugin-scanner/install-with-hol-guard), which checks the [HOL listing](https://hol.org/registry/plugins/mvikmanners%2Faw1-circuit-breaker) and asks before each runtime:

```sh
hol-guard plugin install mvikmanners/aw1-circuit-breaker --apply
```

Get HOL Guard with `pipx install hol-guard` or `uv tool install hol-guard`.

<details>
<summary>Install with each runtime's own CLI</summary>

| Runtime | Commands |
| --- | --- |
| Claude Code | `claude plugin marketplace add mvikmanners/aw1-circuit-breaker`<br>`claude plugin install aw1-circuit-breaker@aw1-circuit-breaker` |
| Codex | `codex plugin marketplace add mvikmanners/aw1-circuit-breaker`<br>`codex plugin add aw1-circuit-breaker@aw1-circuit-breaker` |

</details>
<!-- /hol-install-block -->

## 💳 Cloud Gateway & Commercial Licensing

While the open-source AST circuit breaker runs entirely local with sub-0.2ms overhead, enterprise teams, autonomous agent labs, and fintechs can connect to the hosted **AW-1 Sovereign Cloud Gateway** at `https://p20.laveto.net` for centralized policy orchestration, statutory audit compliance (Bank of Botswana & Botswana DPA 2018), and hardware-enforced out-of-band arbitration.

| Tier | Price | Monthly Quota | Features | Checkout |
| :--- | :--- | :--- | :--- | :--- |
| **Developer Pro** | **BWP 650.00 / mo** ($49 USD) | 100,000 Verified Audits | 1 commercial license key, offline HMAC validation, Layer 0 AST unpacker, community support | [👉 Subscribe Now](https://p20.laveto.net/wisdom/buy) |
| **Team / Startup** | **BWP 2,650.00 / mo** ($199 USD) | 1,000,000 Verified Audits | 5 developer seat keys, Redis distributed state sync, rolling velocity caps, priority alerts | [👉 Subscribe Team](https://p20.laveto.net/wisdom/buy?tier=team) |
| **Enterprise Dedicated** | **BWP 13,200.00 / mo** ($990 USD) | Unlimited Verified Audits | Dedicated gateway tenant, custom statutory risk lenses, SLA guarantees, SHA-256 Decision Assurance Dossiers | [💬 Contact Enterprise](mailto:command@laveto.net) |

*Self-hosted open-source circuit breaking remains 100% free under the Apache-2.0 license.*