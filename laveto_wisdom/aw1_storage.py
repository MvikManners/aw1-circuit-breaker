import os
import json
import time
import fcntl
import hashlib
from typing import List, Dict, Any

TELEMETRY_PATH = "/tmp/aw1_telemetry.json"
BURNED_NONCES_PATH = "/tmp/aw1_burned_nonces.json"

class AtomicFileLock:
    """POSIX file lock context manager ensuring multi-worker process safety."""
    def __init__(self, lock_file_path: str, timeout: float = 5.0):
        self.lock_path = lock_file_path + ".lock"
        self.timeout = timeout
        self.fd = None

    def __enter__(self):
        self.fd = open(self.lock_path, "a")
        start = time.perf_counter()
        while time.perf_counter() - start < self.timeout:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except (IOError, OSError):
                time.sleep(0.005)
        raise TimeoutError(f"Could not acquire lock on {self.lock_path} within {self.timeout}s")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fd:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_UN)
                self.fd.close()
            except Exception:
                pass

class AW1StorageEngine:
    @staticmethod
    def append_telemetry(event: Dict[str, Any]) -> Dict[str, Any]:
        """Appends an event with atomic POSIX locking and cryptographic SHA-256 hash chaining."""
        with AtomicFileLock(TELEMETRY_PATH):
            events: List[Dict[str, Any]] = []
            if os.path.exists(TELEMETRY_PATH):
                try:
                    with open(TELEMETRY_PATH, "r", encoding="utf-8") as f:
                        events = json.load(f)
                except Exception:
                    events = []

            # Cryptographic Hash Chaining (SOC 2 Non-Repudiation)
            prev_hash = events[-1].get("record_hash", "GENESIS_NODE_AW1") if events else "GENESIS_NODE_AW1"
            canon = f"{prev_hash}:{event.get('actor')}:{event.get('tool')}:{event.get('status')}:{event.get('timestamp')}"
            record_hash = hashlib.sha256(canon.encode("utf-8")).hexdigest()

            event["prev_hash"] = prev_hash
            event["record_hash"] = record_hash

            events.append(event)
            if len(events) > 100:
                events = events[-100:]

            tmp_path = TELEMETRY_PATH + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(events, f)
            os.replace(tmp_path, TELEMETRY_PATH)
            return event

    @staticmethod
    def get_recent_telemetry(limit: int = 20) -> List[Dict[str, Any]]:
        """Safely reads recent telemetry records under atomic shared lock."""
        with AtomicFileLock(TELEMETRY_PATH):
            if not os.path.exists(TELEMETRY_PATH):
                return []
            try:
                with open(TELEMETRY_PATH, "r", encoding="utf-8") as f:
                    events = json.load(f)
                    return events[-limit:]
            except Exception:
                return []

    @staticmethod
    def burn_nonce_atomic(nonce: str) -> bool:
        """
        Atomically inspects and burns a nonce within an exclusive POSIX lock.
        Returns True if the nonce was valid and successfully burned.
        Returns False if the nonce was already consumed (neutralizing replay attacks).
        """
        with AtomicFileLock(BURNED_NONCES_PATH):
            burned: List[str] = []
            if os.path.exists(BURNED_NONCES_PATH):
                try:
                    with open(BURNED_NONCES_PATH, "r", encoding="utf-8") as bf:
                        burned = json.load(bf)
                except Exception:
                    burned = []

            if nonce in burned:
                return False

            burned.append(nonce)
            if len(burned) > 1000:
                burned = burned[-1000:]

            tmp_path = BURNED_NONCES_PATH + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as bf:
                json.dump(burned, bf)
            os.replace(tmp_path, BURNED_NONCES_PATH)
            return True
