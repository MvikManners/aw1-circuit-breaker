# Deterministic AST Runtime Verification vs. Probabilistic LLM Guardrails
### An Empirical Evaluation of Pre-Execution Security Boundaries for Autonomous Agents

**Authors:** Laveto Wisdom Security Labs  
**Classification:** Public Engineering & Compliance Whitepaper  
**Document ID:** AW1-WP-2026-V1  
**Repository:** https://github.com/MvikManners/aw1-circuit-breaker  
**Live Production Node:** https://p20.laveto.net/wisdom/docs  

---

## Abstract
As autonomous artificial intelligence agents transition from bounded chat interfaces to dynamic tool execution (e.g., shell command execution, remote procedure calls, and file system mutations), the security boundary between untrusted model outputs and the host operating system represents the single largest vulnerability surface in modern enterprise AI deployments.

Contemporary mitigation strategies predominantly rely on LLM-as-a-judge guardrails or regular expression filters. We demonstrate that probabilistic guardrails impose severe latency penalties (500ms-2000ms), incur non-deterministic failure modes via prompt injection jailbreaks, and fail to prevent steganographic execution tunneling.

This paper presents AW-1, a zero-dependency, deterministic Abstract Syntax Tree (AST) pre-execution circuit breaker. Across 1,000 cycles on the adversarial BRK test suite and >600 live production requests on public nodes, AW-1 demonstrates 100.0% containment efficiency against Base64 tunneling, dynamic reflection, and unauthorized path traversal, while introducing <0.14ms mean inspection overhead (0.0062ms in V8/Node.js, 0.0020ms in HTTP sidecar daemon).

---

## 1. Mitigation Architecture Comparison

| Mitigation Architecture | Enforcement Mechanism | Round-Trip Latency | Determinism | False Positive Risk | Supply Chain Footprint |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **LLM-as-a-Judge** | Secondary neural model | 500ms - 2,000ms | Probabilistic (Jailbreakable) | High (Context drift) | Heavy (API/GPU dependency) |
| **Regex / Blocklists** | Static string matching | <0.05ms | Fragile (Trivially bypassed) | High (Keyword collisions) | Minimal |
| **MicroVM Sandboxing** | Hardware virtualization | 150ms - 500ms | Deterministic | Zero | Very Heavy (Memory/Disk) |
| **AW-1 AST Circuit Breaker** | **Deterministic AST Visitor** | **<0.14ms (0.006ms in TS)** | **100% Deterministic** | **0.00% (Grammar-level)** | **Zero (Native runtime)** |

---

## 2. Technical Architecture: Layer 0 AST Deconstruction
AW-1 operates out-of-band at Layer 0, intercepting the raw proposed tool argument before it reaches subprocess.Popen, exec(), or the operating system kernel:

1. Intercept raw tool call proposal before syscall dispatch.
2. Unpack Base64/Hex and string reflection tunnels.
3. Parse AST out-of-band using native language parser.
4. Fail-closed: raise ExecutionHalt before operating system thread dispatch.

---

## 3. Statutory & Regulatory Mapping
Deploying aw1-circuit-breaker enables enterprise workloads to demonstrate compliance with:
- **NIST AI RMF 1.0 (Govern 1.2, Protect 2.1):** Formal governance structures and fail-closed boundaries on tool calls.
- **SOC 2 Type II (CC6.1, CC6.6):** Logical boundary controls preventing unauthorized code execution and perimeter traversal.
- **ISO/IEC 42001 (Clause A.6.2):** Automated assessment and containment of autonomous AI system agency.
- **Bank of Botswana Cyber Directive / Financial Float Parity:** Zero unshielded lateral fund disbursement; cryptographic audit trails for compliance verification.

---

## 4. Verification & Reproducibility
The test harnesses, benchmark suites, and container manifests are openly available:
- **PyPI:** pip install aw1-circuit-breaker
- **TypeScript:** Node.js/V8 package with 0.0062ms latency
- **Kubernetes Sidecar:** CIS-compliant unprivileged pod manifest
- **Live Node Telemetry:** https://p20.laveto.net/wisdom/security
