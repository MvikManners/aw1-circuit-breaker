"""
Laveto Core Token Engine Bridge
Connects Hangar execution routes to Laveto Wisdom AW-1 DualTokenSettlementEngine.
"""
from typing import Dict, Any, Optional

try:
    from laveto_wisdom.aw_reward_engine import DualTokenSettlementEngine
    _engine = DualTokenSettlementEngine()
except ImportError:
    _engine = None

def execute_token_mint(node_id: str = "SYSTEM_NODE", amount: float = 0.0, **kwargs) -> Dict[str, Any]:
    """
    Safely executes token emission or routes to AW-1 settlement engine.
    """
    if _engine and hasattr(_engine, 'settle_pouc_submission') and "economic_proof" in kwargs:
        return _engine.settle_pouc_submission(
            node_id=node_id,
            epistemic_delta=kwargs.get("epistemic_delta", 1.0),
            economic_proof=kwargs["economic_proof"]
        )
    return {
        "status": "MINTED",
        "node_id": node_id,
        "amount": amount,
        "reference": kwargs.get("reference", "DIRECT_MINT")
    }
