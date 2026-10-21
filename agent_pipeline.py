
# --- AW-1 CREDENTIAL & SHELL HARVESTING INTERCEPTOR (TIER 2) ---
FORBIDDEN_TARGETS = [
    r"id_rsa", r"id_ed25519", r"id_ecdsa", r"\.ssh",
    r"\.env", r"authorized_keys", r"/etc/shadow", r"/etc/passwd",
    r"\.bash_history", r"credentials\.json", r"db_config\.json"
]

DANGEROUS_SHELL_PATTERNS = [
    (r"\brm\s+(-[rfRF]+\s+|-[rR]+\s+-[fF]+\s+)?/", "Destructive root filesystem deletion"),
    (r"\b(mkfs|dd\s+if=)", "Direct block device / disk tampering"),
    (r"(:\(\){ :\|:& };:)", "Fork bomb denial of service"),
    (r"(curl|wget)\s+.*\|\s*(bash|sh)", "Remote unauthorized script piping to shell"),
    (r"\bnc\s+.*-e\s+", "Reverse netcat socket shell execution")
]

def evaluate_host_and_shell_safety(tool_name: str, payload: str) -> tuple[bool, str]:
    # 1. Universal credential scan across all tools
    for pattern in FORBIDDEN_TARGETS:
        if re.search(pattern, payload, re.IGNORECASE):
            return False, f"CRITICAL_CREDENTIAL_HARVESTING_ATTEMPT: '{pattern}'"
            
    # 2. Destructive shell commands
    if any(sh in tool_name.lower() for sh in ["bash", "sh", "terminal", "cmd", "exec"]):
        for pattern, desc in DANGEROUS_SHELL_PATTERNS:
            if re.search(pattern, payload):
                return False, f"CRITICAL_SHELL_PRIMITIVE: {desc}"
                
    return True, "Safe"

import json
import time
import hmac
import hashlib
import urllib.request
import urllib.error
from typing import Dict, Any
from aw1 import guard

class AW1SecurityInterceptionError(Exception):
    def __init__(self, message: str, payload: Dict[str, Any]):
        super().__init__(message)
        self.payload = payload

# Guarded local execution gate: payload evaluated locally fail-closed
@guard
def _guarded_local_dispatch(code_or_payload: str) -> str:
    """Evaluates payload locally through AST engine fail-closed before execution."""
    return code_or_payload

class ProductionAgentPipeline:
    def __init__(
        self,
        gateway_url: str = "https://p20.laveto.net/wisdom/api/v1/intercept",
        actor_id: str = "agent-alpha-01",
        actor_secret: str = "aw1_sec_alpha_9a748be8704e453a10714ce28378dc2f"
    ):
        self.gateway_url = gateway_url
        self.actor_id = actor_id
        self.actor_secret = actor_secret

    def _generate_identity_headers(self, tool_name: str, payload: str) -> Dict[str, str]:
        ts = int(time.time())
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
        msg = f"{ts}:{self.actor_id}:{tool_name}:{digest}".encode("utf-8")
        sig = hmac.new(self.actor_secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()[:32]
        return {
            "Content-Type": "application/json",
            "X-AW1-Actor-Id": self.actor_id,
            "X-AW1-Timestamp": str(ts),
            "X-AW1-Signature": sig
        }

    def intercept_pre_dispatch(self, tool_name: str, payload: str) -> Dict[str, Any]:
        """Queries the AW-1 cloud gateway prior to tool execution."""
        data = json.dumps({
            "actor_id": self.actor_id,
            "tool_name": tool_name,
            "payload": payload
        }).encode("utf-8")

        headers = self._generate_identity_headers(tool_name, payload)
        req = urllib.request.Request(self.gateway_url, data=data, headers=headers)

        start = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                rtt_ms = (time.perf_counter() - start) * 1000
                verdict = json.loads(response.read().decode("utf-8"))
                verdict["network_rtt_ms"] = round(rtt_ms, 2)
                return verdict
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8") if e.fp else str(e)
            raise AW1SecurityInterceptionError(f"Gateway HTTP error {e.code}: {raw}", {})

    def execute_agent_step(self, tool_name: str, payload: str) -> Dict[str, Any]:
        print(f"\n[Agent Pipeline] 🤖 Preparing dispatch: '{tool_name}'")
        print(f"                 Payload: {payload}")

        # Gate 1: Local Sub-Millisecond AST Pre-Check
        _guarded_local_dispatch(payload)

        # Gate 2: Cloud Gateway Interception & Token Minting
        verdict = self.intercept_pre_dispatch(tool_name, payload)

        if verdict.get("status") != "PERMITTED":
            raise AW1SecurityInterceptionError(
                f"Execution Blocked by AW-1 Breaker: {verdict.get('reason')}",
                verdict
            )

        return {
            "status": "EXECUTED",
            "token": verdict.get("token"),
            "gateway_latency_ms": verdict.get("latency_ms"),
            "network_rtt_ms": verdict.get("network_rtt_ms"),
            "result": f"Safely executed {tool_name}"
        }
