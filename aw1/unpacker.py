import base64
import ast
import re
from typing import List, Tuple

class ASTSymbolicUnpacker:
    """
    Decompiles polyglots, base64 strings, and eval wrappers 
    into raw execution primitives prior to tool invocation.
    """
    PAYOUT_KEYWORDS = {"transfer", "payout", "drain", "send", "withdraw", "disburse"}
    CRITICAL_TARGETS = {"hot_wallet", "core_ledger", "treasury", "vault", "reserve"}

    def decompile(self, payload: str) -> Tuple[List[str], str]:
        normalized = payload.strip()
        
        # Check and decode base64 wrapper
        if normalized.startswith("base64:"):
            try:
                b64_content = normalized.split("base64:", 1)[1]
                decoded = base64.b64decode(b64_content).decode("utf-8", errors="ignore")
                normalized = decoded
            except Exception:
                pass

        primitives = []
        lower_payload = normalized.lower()

        # Detect payout intent
        if any(kw in lower_payload for kw in self.PAYOUT_KEYWORDS):
            primitives.append("[FINANCIAL_PAYOUT]")

        # Detect irreversible target
        if any(target in lower_payload for target in self.CRITICAL_TARGETS):
            primitives.append("[HIGH_VALUE_ONE_WAY_DOOR]")

        # Detect eval or shell polyglots
        if "eval(" in lower_payload or "exec(" in lower_payload or "system(" in lower_payload:
            primitives.append("[CODE_EVAL_POLYGLOT]")

        return primitives, normalized
