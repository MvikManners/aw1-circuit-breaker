"""
aw1.breaker
~~~~~~~~~~~
Canonical alias module for aw1.circuit.ExecutionBreaker.
Provides ASTCircuitBreaker backward/forward compatibility.
"""

from .circuit import ExecutionBreaker, ASTSymbolicUnpacker, StatefulCausalMemory

# Canonical alias
ASTCircuitBreaker = ExecutionBreaker

__all__ = [
    "ASTCircuitBreaker",
    "ExecutionBreaker",
    "ASTSymbolicUnpacker",
    "StatefulCausalMemory"
]
