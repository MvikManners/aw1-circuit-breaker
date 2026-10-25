import os
import pathlib
from typing import List, Optional, Set

class EndpointSecurityBreach(PermissionError):
    pass

class HostEndpointDaemon:
    FORBIDDEN_STEMS: Set[str] = {
        "id_rsa", "id_ed25519", "id_ecdsa", "authorized_keys",
        "sam", "system", "security", "ntuser.dat",
        "shadow", "passwd"
    }

    FORBIDDEN_EXACT_NAMES: Set[str] = {
        ".env", "credentials.json", "db_config.json", ".bash_history"
    }

    FORBIDDEN_DIR_SEGMENTS: Set[str] = {
        ".ssh", ".aws", ".azure", ".kube"
    }

    def __init__(
        self,
        workspace_root: str = "/home/LavetoLab/aw1-breaker",
        allowed_egress_domains: Optional[List[str]] = None
    ):
        self.workspace_root = pathlib.Path(workspace_root).resolve()
        self.allowed_domains = allowed_egress_domains or [
            "p20.laveto.net",
            "api.github.com",
            "pypi.org"
        ]

    def validate_path_access(self, target_path: str, write_intent: bool = False) -> str:
        resolved = pathlib.Path(target_path).expanduser().resolve()
        fname = resolved.name.lower()
        fstem = fname.split(".")[0] if "." in fname else fname
        full_posix = resolved.as_posix().lower()
        dir_parts = {p.lower() for p in resolved.parts[:-1]}

        for seg in self.FORBIDDEN_DIR_SEGMENTS:
            if seg in dir_parts or f"/{seg}/" in full_posix:
                raise EndpointSecurityBreach(f"Access denied to sensitive directory segment: {seg}")

        if "/etc/shadow" in full_posix or "/etc/passwd" in full_posix:
            raise EndpointSecurityBreach("Access denied to sensitive system credential path")

        if fname in self.FORBIDDEN_EXACT_NAMES:
            raise EndpointSecurityBreach(f"Access denied to sensitive file: {fname}")

        if fstem in self.FORBIDDEN_STEMS:
            raise EndpointSecurityBreach(f"Access denied to sensitive target pattern: {fstem}")

        if write_intent:
            try:
                resolved.relative_to(self.workspace_root)
            except ValueError:
                raise EndpointSecurityBreach(f"Write target escapes workspace sandbox: {resolved}")

        return str(resolved)

    def validate_network_egress(self, destination_host: str, port: int) -> bool:
        h = destination_host.strip().lower()
        for app in self.allowed_domains:
            if h == app or h.endswith("." + app):
                return True
        raise EndpointSecurityBreach(f"Outbound egress to {h}:{port} blocked by AW-1 policy.")

_daemon_instance = None
def get_endpoint_daemon() -> HostEndpointDaemon:
    global _daemon_instance
    if _daemon_instance is None:
        _daemon_instance = HostEndpointDaemon()
    return _daemon_instance
