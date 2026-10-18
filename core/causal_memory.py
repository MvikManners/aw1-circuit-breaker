"""
Distributed Causal Memory & Multi-Turn Correlation Engine for AW-1 & Laveto Wisdom.
Supports Redis / Valkey clustered backends with transparent in-memory thread-safe fallback.
Provides atomic sliding-window rate limiting and cumulative agent risk tracking.
"""
import os
import time
import json
import logging
import threading
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger("aw1.causal_memory")

class CausalMemoryTier:
    _instance = None
    _lock = threading.RLock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CausalMemoryTier, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, redis_url: Optional[str] = None):
        if getattr(self, "_initialized", False):
            return

        self.redis_url = redis_url or os.getenv("REDIS_URL")
        self.redis_client = None
        self.backend = "in_memory"

        # Initialize In-Memory thread-safe data structures
        self._local_history = defaultdict(deque)     # actor_id -> deque of event dicts
        self._local_rate_limits = defaultdict(deque) # key -> deque of timestamps
        self._local_lock = threading.RLock()

        # Attempt Distributed Redis Backend
        if self.redis_url:
            try:
                import redis
                client = redis.Redis.from_url(
                    self.redis_url,
                    socket_connect_timeout=2.0,
                    socket_timeout=2.0,
                    decode_responses=True
                )
                client.ping()
                self.redis_client = client
                self.backend = "redis"
                logger.info(f"🔗 CausalMemoryTier: Connected to distributed Redis at {self.redis_url}")
            except Exception as e:
                logger.warning(f"⚠️ Redis connection failed ({e}). Defaulting to thread-safe in-memory backend.")
                self.redis_client = None
                self.backend = "in_memory"

        self._initialized = True
        logger.info(f"🧠 CausalMemoryTier active under backend: {self.backend.upper()}")

    def record_action(
        self,
        actor_id: str,
        tool_name: str,
        payload_hash: str,
        decision: str,
        ast_primitives: List[str],
        risk_score: float = 0.0,
        ttl_seconds: int = 3600
    ) -> None:
        """Records an agent audit action into the causal memory graph."""
        now = time.time()
        record = {
            "timestamp": now,
            "tool_name": str(tool_name),
            "payload_hash": str(payload_hash),
            "decision": str(decision),
            "ast_primitives": list(ast_primitives),
            "risk_score": float(risk_score)
        }

        if self.backend == "redis" and self.redis_client:
            try:
                key = f"aw1:causal:{actor_id}"
                self.redis_client.zadd(key, {json.dumps(record): now})
                self.redis_client.expire(key, ttl_seconds)
                return
            except Exception as e:
                logger.warning(f"Redis record_action failed: {e}. Falling back to local store.")

        # In-Memory fallback with eviction
        with self._local_lock:
            q = self._local_history[actor_id]
            q.append(record)
            # Prune records older than ttl_seconds
            cutoff = now - ttl_seconds
            while q and q[0]["timestamp"] < cutoff:
                q.popleft()

    def get_history(self, actor_id: str, window_seconds: int = 600) -> List[Dict[str, Any]]:
        """Retrieves recent action history for an actor within the time window."""
        now = time.time()
        cutoff = now - window_seconds

        if self.backend == "redis" and self.redis_client:
            try:
                key = f"aw1:causal:{actor_id}"
                raw_items = self.redis_client.zrangebyscore(key, cutoff, now)
                return [json.loads(item) for item in raw_items]
            except Exception as e:
                logger.warning(f"Redis get_history failed: {e}. Falling back to local store.")

        with self._local_lock:
            q = self._local_history.get(actor_id, deque())
            return [evt for evt in q if evt["timestamp"] >= cutoff]

    def get_cumulative_risk(self, actor_id: str, window_seconds: int = 600) -> float:
        """Calculates cumulative risk score across recent turns to detect probing drift."""
        history = self.get_history(actor_id, window_seconds)
        total_risk = sum(item.get("risk_score", 0.0) for item in history)
        return round(total_risk, 4)

    def check_rate_limit(
        self,
        identifier: str,
        max_requests: int = 60,
        window_seconds: int = 60
    ) -> Tuple[bool, int, float]:
        """
        Atomic sliding-window rate limiter.
        Returns: (allowed: bool, current_count: int, retry_after: float)
        """
        now = time.time()
        cutoff = now - window_seconds

        if self.backend == "redis" and self.redis_client:
            try:
                key = f"aw1:ratelimit:{identifier}"
                pipe = self.redis_client.pipeline()
                pipe.zremrangebyscore(key, 0, cutoff)
                pipe.zcard(key)
                pipe.zadd(key, {f"{now}": now})
                pipe.expire(key, window_seconds + 5)
                results = pipe.execute()

                current_count = results[1]
                if current_count >= max_requests:
                    # Remove the tentatively added item
                    self.redis_client.zrem(key, f"{now}")
                    return False, current_count, round(window_seconds - (now - cutoff), 2)
                return True, current_count + 1, 0.0
            except Exception as e:
                logger.warning(f"Redis rate-limit failed: {e}. Falling back to local store.")

        # In-Memory thread-safe atomic sliding window
        with self._local_lock:
            timestamps = self._local_rate_limits[identifier]
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

            current_count = len(timestamps)
            if current_count >= max_requests:
                oldest = timestamps[0]
                retry_after = round(max(0.1, window_seconds - (now - oldest)), 2)
                return False, current_count, retry_after

            timestamps.append(now)
            return True, current_count + 1, 0.0

    def purge(self, actor_id: Optional[str] = None):
        """Clears memory for a specific actor or all actors."""
        if self.backend == "redis" and self.redis_client:
            try:
                if actor_id:
                    self.redis_client.delete(f"aw1:causal:{actor_id}")
                    self.redis_client.delete(f"aw1:ratelimit:{actor_id}")
                else:
                    keys = self.redis_client.keys("aw1:*")
                    if keys:
                        self.redis_client.delete(*keys)
            except Exception:
                pass

        with self._local_lock:
            if actor_id:
                self._local_history.pop(actor_id, None)
                self._local_rate_limits.pop(actor_id, None)
            else:
                self._local_history.clear()
                self._local_rate_limits.clear()

# Global Singleton Accessor
causal_memory = CausalMemoryTier()
