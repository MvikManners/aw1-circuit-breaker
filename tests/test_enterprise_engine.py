import os
import sys
import subprocess
import pytest

def test_unified_platform_verification():
    # Automatically add repo root and parent paths to PYTHONPATH
    env = os.environ.copy()
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env["PYTHONPATH"] = root_dir + ":" + env.get("PYTHONPATH", "")
    
    # Also add standard Laveto Wisdom search paths if present
    for p in ["/home/LavetoLab", "/home/LavetoLab/lvt_backend", "/home/LavetoLab/laveto_wisdom"]:
        if os.path.exists(p) and p not in env["PYTHONPATH"]:
            env["PYTHONPATH"] = p + ":" + env["PYTHONPATH"]

    print(f"Running unified verification with PYTHONPATH={env['PYTHONPATH']}")
    result = subprocess.run(["bash", "test_all.sh"], capture_output=True, text=True, env=env)
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)
    assert result.returncode == 0, f"Unified platform verification failed with exit code {result.returncode}"
