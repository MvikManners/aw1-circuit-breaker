import time
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

class StatefulCausalMemory:
    """
    Layer 1: Stateful Causal Memory & Rolling Velocity Windows.
    Enforces multi-turn velocity caps and neutralizes Salami Micro-Call state drift.
    """
    def __init__(self, baseline_velocity_limit: float = 50000.0, window_seconds: float = 86400.0):
        self.baseline_velocity_limit = float(baseline_velocity_limit)
        self.window_seconds = float(window_seconds)
        self._history: Dict[str, List[Tuple[float, float]]] = defaultdict(list)

    def record_and_evaluate(self, actor_id: str, amount: float = 0.0) -> Tuple[bool, float, Optional[str]]:
        now = time.time()
        cutoff = now - self.window_seconds
        
        # Prune events older than the rolling window
        valid_history = [item for item in self._history[actor_id] if item[0] >= cutoff]
        self._history[actor_id] = valid_history

        accumulated = sum(item[1] for item in valid_history) + float(amount)
        ratio = (accumulated / self.baseline_velocity_limit) if self.baseline_velocity_limit > 0 else 0.0

        if self.baseline_velocity_limit > 0 and accumulated > self.baseline_velocity_limit:
            reason = f"Stateful velocity limit breached: accumulated {accumulated:.2f} exceeds limit {self.baseline_velocity_limit:.2f}"
            return False, ratio, reason

        # Record permitted event
        self._history[actor_id].append((now, float(amount)))
        return True, ratio, "Stateful velocity within normal boundaries"

    def get_velocity(self, actor_id: str) -> float:
        now = time.time()
        cutoff = now - self.window_seconds
        return sum(item[1] for item in self._history.get(actor_id, []) if item[0] >= cutoff)

    def reset(self, actor_id: Optional[str] = None):
        if actor_id:
            self._history.pop(actor_id, None)
        else:
            self._history.clear()
