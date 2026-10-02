"""
tests/test_daemon.py
Comprehensive adversarial & isolation test suite for aw1-daemon (Phase 2 & 3).
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from aw1_daemon.core import AW1Daemon

WORKSPACE = "/tmp/aw1_safe_workspace"

@pytest.fixture
def daemon():
    os.makedirs(WORKSPACE, exist_ok=True)
    return AW1Daemon(workspace_path=WORKSPACE)

def test_ast_injection_blocked(daemon):
    malicious_code = "__import__('os').system('rm -rf /')"
    result = daemon.intercept(malicious_code)
    assert result["status"] == "BLOCKED"
    assert result["gate"] == "GATE_7_AST_BREAKER"
    assert "incident_id" in result

def test_sensitive_path_blocked(daemon):
    safe_code = "print('Reading configs...')"
    result = daemon.intercept(safe_code, target_paths=["~/.ssh/id_rsa"])
    assert result["status"] == "BLOCKED"
    assert "sensitive target" in result["reason"]
    assert "incident_id" in result

def test_benign_workspace_allowed(daemon):
    benign_code = "print('Processing data...')"
    safe_file = os.path.join(WORKSPACE, "app.py")
    result = daemon.intercept(benign_code, target_paths=[safe_file])
    assert result["status"] == "ALLOWED"
    assert "token" in result

def test_ephemeral_sandbox_isolation(daemon):
    # Safe code that writes a temporary file inside the sandbox
    safe_isolated_code = """
import os
with open("local_leak_test.txt", "w") as f:
    f.write("sandbox-test-data")
print("WROTE_SUCCESS")
"""
    result = daemon.execute_in_sandbox(safe_isolated_code)
    assert result["status"] == "COMPLETED"
    assert "WROTE_SUCCESS" in result["stdout"]
    # Verify the temporary sandbox was completely purged from the system
    assert not os.path.exists(result["sandbox_path"])
