# AW-1 Security Policy & Responsible Vulnerability Disclosure

## 1. Deterministic Safety Commitment
Laveto Wisdom Security Labs maintains aw1-circuit-breaker as a deterministic, zero-dependency Layer 0 security standard for autonomous AI agents and Model Context Protocol (MCP) tool servers.

## 2. In-Scope Targets
- PyPI Package: aw1-circuit-breaker
- TypeScript SDK: aw1-circuit-breaker-ts
- Sidecar Daemon: aw1-sidecar
- Live Node: https://p20.laveto.net/wisdom/

## 3. Severity & SLA
- CRITICAL: AST bypass leading to host command execution (24h response / 48h patch).
- HIGH: Steganographic or reflection evasions reading host environment (48h response / 5d patch).
- MEDIUM: Resource starvation causing >5ms latency on valid inputs (72h response / 10d patch).

## 4. 'Break the Breaker' Bug Bounty Program
Researchers who submit a reproducible script bypassing the AST circuit breaker boundary receive:
1. Security Hall of Fame entry.
2. Co-authorship credit in the remediation patch.
3. Direct institutional bounty compensation according to assessed CVSS score.

## 5. Reporting
Submit proof-of-concept payloads to: security@laveto.net or via https://p20.laveto.net/wisdom/security
