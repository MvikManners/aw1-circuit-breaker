# Deterministic Containment of Autonomous Tool-Using Agents via Out-of-Band AST Primitive Deconstruction and Heterogeneous Multi-Model Arbitration

**Authors:** Laveto Wisdom Research Group (AW-1 Project)
**Target Tracks:** arXiv:cs.AI | arXiv:cs.CR | AI Alignment Forum
**Date:** October 2026
**Artifact Codebase:** github.com/MvikManners/aw1-circuit-breaker (release: v1.0.0-statutory-compliance)

---

### Abstract
Contemporary safety frameworks for autonomous foundation-model agents rely predominantly on in-band semantic defenses (RLHF, system prompts, secondary LLM evaluators). When agents operate in multi-turn environments with shell access, dynamic interpretation, and external tool-calling capabilities, these probabilistic guardrails exhibit catastrophic failure modes under adversarial optimization and steganographic tunneling.

We present AW-1, an independent, out-of-band execution circuit breaker that decouples cognitive model reasoning from physical and network execution authority. Sitting strictly out-of-band at the API gateway layer, AW-1 intercepts proposed agent tool payloads prior to execution using a zero-trust proxy architecture.

Key contributions:
1. Layer 0 AST Symbolic Unpacker: Deterministically decompiles serialized tool calls, Base64 strings, and dynamic eval() routines into standardized hardware/OS primitives ([NETWORK_EGRESS], [KERNEL_WRITE], [PRIVILEGE_ESCALATE], [SOCKET_BIND]) with sub-millisecond overhead (<0.50ms).
2. Heterogeneous Council Arbitration & Disagreement-Halts: High-uncertainty actions are evaluated concurrently across a symbolic logic checker, contextual foundation model, and adversarial red-team evaluator. If variance sigma^2 > tau, Gate 4 freezes execution unconditionally.

Benchmarked against the BRK Breakout Suite (BRK-101 Base64 log-spoofing, BRK-102 socket egress, BRK-103 kernel privilege rewrites), achieving 100% containment across 1,000 adversarial trial runs with SHA-256 sealed JSON-LD audit dossiers.
