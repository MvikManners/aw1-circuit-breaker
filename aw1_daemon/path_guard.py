"""
aw1_daemon/path_guard.py
Deterministic host filesystem containment for autonomous agents.
"""
import os
from typing import Tuple

BLOCKED_PATTERNS = [
    ".ssh",
    ".aws",
    ".gnupg",
    ".env",
    "id_rsa",
    "/etc/passwd",
    "/etc/shadow",
    "sudoers"
]

class PathGuard:
    def __init__(self, allowed_workspace: str):
        self.allowed_workspace = os.path.abspath(allowed_workspace)

    def is_path_safe(self, target_path: str) -> Tuple[bool, str]:
        normalized = os.path.abspath(os.path.expanduser(target_path))
        
        # 1. Hard-blocked credentials / system paths
        for pattern in BLOCKED_PATTERNS:
            if pattern in normalized:
                return False, f"Access to sensitive target '{pattern}' is prohibited by AW-1."

        # 2. Workspace boundary check
        if not normalized.startswith(self.allowed_workspace):
            return False, f"Path '{normalized}' is outside authorized workspace '{self.allowed_workspace}'."

        return True, "SAFE"
