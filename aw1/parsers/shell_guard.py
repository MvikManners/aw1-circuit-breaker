import re
from typing import Optional, Tuple

class ShellGuard:
    SHELL_RISK_PATTERNS = [
        (re.compile(r'\|\s*(bash|sh|zsh)\b', re.I), "[SHELL_PIPE_EXECUTION]"),
        (re.compile(r'\bcurl\b.*\|\s*(bash|sh)', re.I), "[SHELL_CURL_PIPE_EXEC]"),
        (re.compile(r'\bwget\b.*\|\s*(bash|sh)', re.I), "[SHELL_WGET_PIPE_EXEC]"),
        (re.compile(r'\brm\s+-[rR][fF]\b', re.I), "[SHELL_RECURSIVE_FORCE_DELETE]"),
        (re.compile(r'>\s*/etc/', re.I), "[SHELL_SYSFS_OVERWRITE]"),
    ]

    @classmethod
    def inspect(cls, payload: str) -> Optional[Tuple[str, str]]:
        clean = payload.strip()
        for pattern, primitive in cls.SHELL_RISK_PATTERNS:
            if pattern.search(clean):
                return primitive, f"Dangerous shell command detected matching primitive {primitive}"
        return None
