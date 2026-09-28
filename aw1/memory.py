import time
from collections import defaultdict
from typing import Dict, List, Tuple

class StatefulCausalMemory:
    """
    Maintains rolling velocity profiles per actor to block
    Salami-style micro-exfiltrations and sudden baseline spikes.
    """
    def __init__(self, baseline_velocity_limit: float = 50000.0, window_seconds: int = 2592000):
        self.baseline_velocity_limit = baseline_velocity_limit
        self.window_seconds = window_seconds  # Default: 30 days
        self.actor_logs: Dict[str, List[Tuple[float, float]]] = defaultdict(list)

    def record_and_evaluate(self, actor_id: str, amount: float) -> Tuple[bool, float, str]:
        now = time.time()
        cutoff = now - self.window_seconds
        
        # Filter rolling window
        self.actor_logs[actor_id] = [
            (ts, val) for ts, val in self.actor_logs[actor_id] if ts >= cutoff
        ]
        
        # Calculate recent velocity
        total_recent = sum(val for _, val in self.actor_logs[actor_id])
        current_spike_ratio = (total_recent + amount) / self.baseline_velocity_limit

        if current_spike_ratio > 1.0:
            return False, current_spike_ratio, f"VELOCITY_SPIKE_DETECTED ({current_spike_ratio:.1f}x threshold limit)"

        self.actor_logs[actor_id].append((now, amount))
        return True, current_spike_ratio, "WITHIN_BASELINE"
