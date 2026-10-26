# Privacy Policy for aw1-circuit-breaker

`aw1-circuit-breaker` is a local-first, zero-dependency Python security circuit breaker.

- **Local Execution:** All Abstract Syntax Tree (AST) policy inspections run strictly in-memory on the host machine.
- **No Inherent Telemetry:** The core engine does not collect, harvest, or transmit code snippets or tool arguments to any remote cloud servers.
- **Optional Gateway:** If configured to use an external arbitration proxy, only explicitly supplied actor IDs and tool execution parameters are routed over TLS.
- **License:** Apache License 2.0.
