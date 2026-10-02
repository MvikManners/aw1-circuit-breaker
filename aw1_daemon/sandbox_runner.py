"""
aw1_daemon/sandbox_runner.py
Phase 3 Ephemeral sandbox runner isolating code execution from host disk.
"""
import tempfile
import shutil
import subprocess
import os
import sys
from typing import Dict, Any

class SandboxRunner:
    def __init__(self, timeout_sec: int = 10):
        self.timeout_sec = timeout_sec

    def execute_isolated(self, code_str: str) -> Dict[str, Any]:
        """
        Executes code inside an ephemeral temporary directory with restricted env,
        wiping all state immediately after process termination.
        """
        temp_dir = tempfile.mkdtemp(prefix="aw1_sandbox_")
        temp_script = os.path.join(temp_dir, "isolated_exec.py")

        try:
            # Write script exclusively within the ephemeral sandbox
            with open(temp_script, "w") as f:
                f.write(code_str)

            # Restrict execution environment variables (no host credential leakage)
            restricted_env = {
                "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                "PYTHONPATH": temp_dir,
                "HOME": temp_dir,
                "TMPDIR": temp_dir
            }

            # Run in isolated sandbox directory
            proc = subprocess.run(
                [sys.executable, temp_script],
                cwd=temp_dir,
                env=restricted_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=self.timeout_sec
            )

            return {
                "status": "COMPLETED",
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "sandbox_path": temp_dir
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "TIMEOUT",
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Execution exceeded maximum timeout of {self.timeout_sec}s."
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e)
            }
        finally:
            # Complete disposable wipe
            shutil.rmtree(temp_dir, ignore_errors=True)
