import hashlib
import hmac
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Dict, Any, Optional

class EphemeralExecutionError(RuntimeError):
    pass

class EphemeralRunner:
    SENSITIVE_ENV_VARS = {
        "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN",
        "GITHUB_TOKEN", "GH_TOKEN", "SSH_AUTH_SOCK", "AZURE_CLIENT_SECRET",
        "DATABASE_URL", "DB_PASSWORD", "ANTHROPIC_API_KEY", "OPENAI_API_KEY",
        "AW1_ACTOR_SECRET", "SLACK_BOT_TOKEN"
    }

    def __init__(self, secret_key: str = "aw1_sec_alpha_9a748be8704e453a10714ce28378dc2f"):
        self.secret_key = secret_key

    def verify_execution_token(self, token: str, actor_id: str, tool_name: str, payload: str) -> bool:
        if not token or not token.startswith("aw1_v1_"):
            return False
        parts = token.split("_")
        if len(parts) < 4:
            return False
        try:
            ts = int(parts[2])
            provided_sig = parts[3]
        except (ValueError, IndexError):
            return False

        if abs(time.time() - ts) > 30:
            return False

        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
        msg = f"{ts}:{actor_id}:{tool_name}:{digest}".encode("utf-8")
        expected_sig = hmac.new(self.secret_key.encode("utf-8"), msg, hashlib.sha256).hexdigest()[:32]
        return hmac.compare_digest(provided_sig, expected_sig)

    def _get_sanitized_environment(self) -> Dict[str, str]:
        clean_env = dict(os.environ)
        for var in self.SENSITIVE_ENV_VARS:
            clean_env.pop(var, None)
        clean_env["AW1_SANDBOX_ISOLATED"] = "1"
        return clean_env

    def execute_in_jail(
        self,
        token: str,
        actor_id: str,
        tool_name: str,
        payload: str,
        timeout_seconds: float = 5.0
    ) -> Dict[str, Any]:
        t0 = time.perf_counter()

        if not self.verify_execution_token(token, actor_id, tool_name, payload):
            return {
                "verdict": "FAIL_CLOSED",
                "status": "HALT_AND_CONTAIN",
                "permitted": False,
                "reason": "Token Gate Rejection: Missing, expired, or counterfeit aw1_v1 token",
                "stdout": "",
                "stderr": "",
                "exit_code": -1,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 4)
            }

        temp_dir = tempfile.mkdtemp(prefix="aw1_jail_")
        jail_path = pathlib.Path(temp_dir).resolve()
        clean_env = self._get_sanitized_environment()
        clean_tool = tool_name.lower().strip()

        if "bash" in clean_tool or "sh" in clean_tool:
            cmd = ["/bin/bash", "-c", payload]
        elif "python" in clean_tool:
            cmd = [sys.executable, "-c", payload]
        else:
            shutil.rmtree(jail_path, ignore_errors=True)
            return {
                "verdict": "FAIL_CLOSED",
                "status": "HALT_AND_CONTAIN",
                "permitted": False,
                "reason": f"Unsupported runner runtime: {tool_name}",
                "stdout": "",
                "stderr": "",
                "exit_code": -1,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 4)
            }

        stdout_data, stderr_data = "", ""
        exit_code = 0
        timed_out = False

        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(jail_path),
                env=clean_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            try:
                stdout_data, stderr_data = proc.communicate(timeout=timeout_seconds)
                exit_code = proc.returncode
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout_data, stderr_data = proc.communicate()
                exit_code = -9
                timed_out = True
        except Exception as exc:
            return {
                "verdict": "ERROR",
                "status": "RUNTIME_FAULT",
                "permitted": False,
                "reason": f"Ephemeral spawn error: {exc}",
                "stdout": "",
                "stderr": str(exc),
                "exit_code": -1,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 4)
            }
        finally:
            shutil.rmtree(jail_path, ignore_errors=True)

        duration_ms = round((time.perf_counter() - t0) * 1000, 3)

        if timed_out:
            return {
                "verdict": "TIMEOUT_KILLED",
                "status": "HALT_AND_CONTAIN",
                "permitted": False,
                "reason": f"Process execution exceeded hard ceiling of {timeout_seconds}s",
                "stdout": stdout_data.strip(),
                "stderr": stderr_data.strip(),
                "exit_code": exit_code,
                "latency_ms": duration_ms
            }

        return {
            "verdict": "EXECUTED",
            "status": "COMPLETED",
            "permitted": True,
            "stdout": stdout_data.strip(),
            "stderr": stderr_data.strip(),
            "exit_code": exit_code,
            "latency_ms": duration_ms
        }

_runner_instance = None
def get_ephemeral_runner() -> EphemeralRunner:
    global _runner_instance
    if _runner_instance is None:
        _runner_instance = EphemeralRunner()
    return _runner_instance
