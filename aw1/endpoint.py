import os
import re
import socket
import pathlib
from typing import List, Optional, Set

class EndpointSecurityBreach(PermissionError):
    """Raised fail-closed when an agent attempts unauthorized host access."""
    pass

class HostEndpointDaemon:
    """
    AW-1 Host-Level Endpoint Protection Daemon.
    Enforces deterministic filesystem sandboxing and network egress boundaries.
    """
    
    DEFAULT_FORBIDDEN_FILES: Set[str] = {
        ".env", "id_rsa", "id_ed25519", "authorized_keys",
        "/etc/passwd", "/etc/shadow", "credentials.json",
        ".bash_history", ".ssh", "db_config.json"
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
        try:
            resolved = pathlib.Path(target_path).expanduser().resolve()
        except Exception as exc:
            raise EndpointSecurityBreach(f"Malformed path rejected fail-closed: {exc}")

        resolved_str = str(resolved)

        for forbidden in self.DEFAULT_FORBIDDEN_FILES:
            if forbidden in resolved_str:
                raise EndpointSecurityBreach(
                    f"Host Containment Alert: Access denied to sensitive file pattern '{forbidden}'"
                )

        if write_intent:
            if not resolved_str.startswith(str(self.workspace_root)):
                raise EndpointSecurityBreach(
                    f"Host Containment Alert: Write target '{resolved_str}' escapes workspace sandbox '{self.workspace_root}'"
                )

        return resolved_str

    def validate_network_egress(self, destination_host: str, port: int) -> bool:
        clean_host = destination_host.strip().lower()
        for approved in self.allowed_domains:
            if clean_host == approved or clean_host.endswith("." + approved):
                return True

        raise EndpointSecurityBreach(
            f"Host Egress Alert: Outbound connection to '{clean_host}:{port}' blocked by AW-1 policy."
        )

_daemon_instance = None

def get_endpoint_daemon() -> HostEndpointDaemon:
    global _daemon_instance
    if _daemon_instance is None:
        _daemon_instance = HostEndpointDaemon()
    return _daemon_instance
