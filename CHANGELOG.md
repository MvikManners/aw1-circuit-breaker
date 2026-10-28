# Changelog

All notable changes to the AW-1 Circuit Breaker will be documented in this file.

## [2.1.0] - 2026-10-21

### Added
- **Universal `@guard` Framework Adapter**: Drop-in wrapper supporting sync functions, `async def` coroutines, and structured agent tool payloads (OpenAI, Anthropic, LangChain, CrewAI).
- **Declarative Policy-as-Code Engine (`SecurityPolicy`)**: Supports JSON/YAML manifests, DoS AST complexity limits (node counts and depth caps), and dynamic `mtime`-based hot reloading.
- **Reflection / Sandbox Escape Defense**: Strict AST gating of dunder attributes (`__subclasses__`, `__globals__`, `__code__`, `__builtins__`).
- **Structured Audit Telemetry**: Microsecond-resolution JSON logging for Datadog, AWS CloudWatch, and OpenTelemetry collectors.
- **Enterprise CI Matrix**: Multi-version GitHub Actions workflow testing Python 3.10, 3.11, 3.12, and 3.13.

### Benchmarks
- Validated at **8,485 dispatches/sec** with **0.0776 ms P50 latency** and sub-0.13 ms fail-closed attack blocking.

---
