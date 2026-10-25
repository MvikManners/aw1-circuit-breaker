import os
import sys
import subprocess
import pytest

def test_unified_platform_verification():
    # Ensure current dir and parent dirs are in PYTHONPATH
    env = os.environ.copy()
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env["PYTHONPATH"] = current_dir + ":" + env.get("PYTHONPATH", "")
    
    result = subprocess.run(["bash", "test_all.sh"], capture_output=True, text=True, env=env)
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)
    assert result.returncode == 0, f"Unified platform verification failed with code {result.returncode}"
