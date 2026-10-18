#!/usr/bin/env python3
"""
AW-1 Deterministic AST Circuit Breaker — Model Context Protocol (MCP) Server.
Provides real-time AST safety deconstruction, threat containment, and policy enforcement
for autonomous agent tool execution.
"""
import sys
from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("aw1-circuit-breaker")

# Lazy-loaded singleton breaker
_breaker = None

def get_breaker():
    global _breaker
    if _breaker is None:
        from aw1 import ASTCircuitBreaker
        _breaker = ASTCircuitBreaker()
    return _breaker

@mcp.tool()
def intercept_tool_call(
    actor_id: str,
    tool_name: str,
    payload: str
) -> Dict[str, Any]:
    """
    Intercept and evaluate an autonomous AI agent tool execution payload before runtime invocation.
    Determines whether the execution is safe or requires immediate containment.

    Args:
        actor_id: Unique identifier or name of the calling agent, user, or process.
        tool_name: The target tool, environment, or command type (e.g., 'bash', 'sql', 'python', 'eval').
        payload: The raw code, shell command, query, or parameters to be inspected by the circuit breaker.

    Returns:
        Dictionary containing the security verdict ('PERMITTED' or 'HALT_AND_CONTAIN'),
        authorization status, cryptographic execution token (if permitted), risk score,
        and detected AST primitives.
    """
    cb = get_breaker()
    verdict = cb.intercept(actor_id=actor_id, tool_name=tool_name, payload=payload)
    return {
        "status": verdict.status,
        "permitted": verdict.status == "PERMITTED",
        "token": verdict.token,
        "reason": getattr(verdict, "reason", "Policy evaluation completed"),
        "risk_score": getattr(verdict, "risk_score", 0.0),
        "primitives": getattr(verdict, "primitives", [])
    }

@mcp.tool()
def analyze_code_ast(
    code: str,
    environment: str = "python"
) -> Dict[str, Any]:
    """
    Deconstruct source code or commands into abstract syntax tree (AST) primitives to detect dangerous patterns.
    Identifies dynamic evaluations, shell piping, lateral network egress, and destructive operations.

    Args:
        code: The source code snippet, query, or command string to statically analyze.
        environment: The syntactic context or execution environment ('python', 'bash', 'sql'). Default is 'python'.

    Returns:
        Dictionary containing detected execution primitives, security classification, and containment recommendations.
    """
    cb = get_breaker()
    verdict = cb.intercept(actor_id="ast-analyzer", tool_name=environment, payload=code)
    return {
        "environment": environment,
        "safe": verdict.status == "PERMITTED",
        "detected_primitives": getattr(verdict, "primitives", []),
        "verdict": verdict.status
    }

@mcp.tool()
def get_circuit_breaker_telemetry() -> Dict[str, Any]:
    """
    Retrieve operational status, active defense policies, and telemetry for the AW-1 Circuit Breaker.

    Returns:
        Dictionary with engine version, status, registered containment layers, and SLA guarantees.
    """
    return {
        "engine": "AW-1 Sovereign Execution Arbitrator",
        "version": "0.2.1",
        "status": "OPERATIONAL",
        "policy_gates": [
            "Layer 0: AST Symbolic Unpacker",
            "Layer 1: Stateful Causal Memory",
            "Layer 2: Multi-Turn Probing Interlock",
            "Gate 7: Hard Containment Circuit Breaker"
        ],
        "zero_dependency_core": True,
        "sla_latency_target_ms": "< 0.50"
    }

if __name__ == "__main__":
    mcp.run()
