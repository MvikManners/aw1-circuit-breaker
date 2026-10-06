# AW-1 Circuit Breaker

[![Apache 2.0 License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![MvikManners/aw1-circuit-breaker MCP server](https://glama.ai/mcp/servers/MvikManners/aw1-circuit-breaker/badges/score.svg)](https://glama.ai/mcp/servers/MvikManners/aw1-circuit-breaker)

Deterministic AST deconstruction and runtime circuit breaker preventing rogue shell escapes, dynamic eval(), and covert lateral socket egress in autonomous LLM tool calls.

## Installation

```bash
pip install -r requirements.txt
```

## Running the Server

Run directly with Python:

```bash
python mcp_server.py
```

Or via uvx:

```bash
uvx mcp_server.py
```

## MCP Client Configuration

```json
{
  "mcpServers": {
    "aw1-circuit-breaker": {
      "command": "python",
      "args": ["mcp_server.py"]
    }
  }
}
```

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
