import subprocess
import pytest

def test_unified_platform_verification():
    # Execute the master verification suite runner
    result = subprocess.run(["bash", "test_all.sh"], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 0, "Unified platform verification harness failed!"
