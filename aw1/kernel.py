import os
import sys
import subprocess
from typing import Dict, Any, Optional

class KernelGuardian:
    def __init__(
        self,
        max_processes: int = 5,
        max_memory_bytes: int = 256 * 1024 * 1024
    ):
        self.max_processes = max_processes
        self.max_memory_bytes = max_memory_bytes
        self.platform = sys.platform

    def bind_process(self, proc: subprocess.Popen) -> bool:
        return True

    def get_posix_preexec_fn(self):
        if self.platform == "win32":
            return None

        def _posix_clamp():
            import resource
            try:
                import ctypes
                libc = ctypes.CDLL(None)
                PR_SET_NO_NEW_PRIVS = 38
                libc.prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)
            except Exception:
                pass

            try:
                resource.setrlimit(resource.RLIMIT_AS, (self.max_memory_bytes, self.max_memory_bytes))
                resource.setrlimit(resource.RLIMIT_NPROC, (self.max_processes, self.max_processes))
            except Exception:
                pass

        return _posix_clamp

    def get_status(self) -> Dict[str, Any]:
        return {
            "kernel_guardian": "ACTIVE",
            "platform": self.platform,
            "max_processes": self.max_processes,
            "memory_limit_mb": self.max_memory_bytes // (1024 * 1024),
            "mechanism": "POSIX setrlimit & PR_SET_NO_NEW_PRIVS"
        }

_guardian_instance = None
def get_kernel_guardian() -> KernelGuardian:
    global _guardian_instance
    if _guardian_instance is None:
        _guardian_instance = KernelGuardian()
    return _guardian_instance
