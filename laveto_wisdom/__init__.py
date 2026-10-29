"""
AW-1 Sovereign Agent Circuit Breaker & Execution Guard
Enterprise AI Security Middleware (v2.0.0)
"""

from laveto_wisdom.breaker import ExecutionBreaker, SecurityTripwireException
from laveto_wisdom.canary import SyntheticCanary
from laveto_wisdom.quorum import QuorumEngine, QuorumVerificationError
from laveto_wisdom.statutory import StatutoryLensEngine
from laveto_wisdom.synthesizer import RuleSynthesizer
from laveto_wisdom.tee import TEEAttestationEngine
from laveto_wisdom.middleware import protect_tool, LangChainAW1Callback
from laveto_wisdom.mcp_server import AW1MCPServer

__version__ = "2.0.0"
__all__ = [
    "ExecutionBreaker",
    "SecurityTripwireException",
    "SyntheticCanary",
    "QuorumEngine",
    "QuorumVerificationError",
    "StatutoryLensEngine",
    "RuleSynthesizer",
    "TEEAttestationEngine",
    "protect_tool",
    "LangChainAW1Callback",
    "AW1MCPServer",
]
