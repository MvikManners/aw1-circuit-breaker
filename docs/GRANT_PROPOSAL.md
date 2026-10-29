# Grant Proposal: AW-1 Deterministic Execution Guard & AST Circuit Breaker

**Target Programs:** GitHub Secure Open Source Fund | OpenSSF Alpha-Omega Project | NLnet Foundation  
**Applicant:** Mvik Manners  
**Repository:** https://github.com/MvikManners/aw1-circuit-breaker  
**License:** MIT (OSI-Approved)  
**Standard Ecosystem Alignment:** Model Context Protocol (MCP) / Agentic AI Foundation (AAIF)  
**Verification:** Glama Grade A Verified (83%) | Listed on `awesome-mcp-servers` (#15832)

---

## 1. Executive Summary

Autonomous agent frameworks increasingly invoke dynamic terminal execution, local file system manipulation, and outbound network connections via the Model Context Protocol (MCP). Current containment patterns rely on non-deterministic LLM-as-a-judge evaluators, introducing high token overhead, 500ms+ network latency, and severe susceptibility to prompt-injection jailbreaks. 

**AW-1** is an open-source, deterministic runtime circuit breaker that operates as local middleware directly ahead of tool-call dispatch. By decomposing payload code into an Abstract Syntax Tree (AST) in sub-0.2 milliseconds, AW-1 programmatically detects and halts dangerous execution vectors—including dynamic `eval()`, obfuscated shell breakouts (`subprocess`, `os.system`), and covert socket egress—before payload dispatch occurs. Operating with zero external network dependencies and zero token consumption, AW-1 provides verifiable, fail-closed safety for unattended autonomous agents across local and cloud environments. 

This grant supports hardening AW-1’s static analysis engine, standardizing AST-level security heuristics across the MCP ecosystem, and publishing an automated regression test suite for adversarial agent exploits.

---

## 2. Problem Statement & Threat Model

As autonomous agents transition from read-only assistants to unattended workflow executors, the attack surface shifts from conversational prompt leakage to **remote runtime code execution (RCE) via tool-call weaponization**:

* **Non-Deterministic Defense Latency:** Asking an LLM to evaluate whether a tool parameter is malicious costs 300–800 tokens and adds 400–1,200 ms of latency per execution step, encouraging developers to disable security checks entirely in production.
* **Obfuscation and Jailbreak Vulnerabilities:** Adversarial prompt injections consistently bypass semantic safety filters through base64 encoding, hex concatenation, or indirect string synthesis designed to evade prompt-level classifiers.
* **Covert Lateral Movement:** Compromised autonomous tools frequently attempt unauthorized socket connections (`socket.connect()`, raw curl invocations) to exfiltrate local environment variables and API credentials.

AW-1 addresses these failure modes by enforcing **deterministic static verification** at the runtime boundary, treating LLM-generated arguments as untrusted user input that must pass strict structural parsing before hitting the OS.

---

## 3. Technical Architecture & Defense Mechanism

AW-1 operates as lightweight Python middleware positioned between the agent orchestrator (e.g., Claude Desktop, LangGraph, AutoGen) and MCP execution backends:
