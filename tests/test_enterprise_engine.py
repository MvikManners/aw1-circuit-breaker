import pytest
import asyncio
from aw1 import guard
from aw1.policy import configure_policy, DEFAULT_POLICY

@pytest.fixture(autouse=True)
def reset_policy():
    """Ensure every test executes against a fresh enterprise default policy."""
    configure_policy(policy_data=DEFAULT_POLICY)

def test_guard_allows_safe_code():
    @guard
    def safe_runner(code: str) -> str:
        return "SUCCESS"

    result = safe_runner("x = [i * 2 for i in range(10)]")
    assert result == "SUCCESS"

def test_guard_blocks_subshell_injection():
    @guard
    def guarded_runner(code: str):
        return "EXECUTED"

    with pytest.raises(PermissionError) as exc_info:
        guarded_runner('import subprocess; subprocess.run(["ls"])')
    assert "Prohibited module import: subprocess" in str(exc_info.value)

def test_guard_blocks_reflection_exploit():
    @guard
    def guarded_runner(code: str):
        return "EXECUTED"

    with pytest.raises(PermissionError) as exc_info:
        guarded_runner("classes = ().__class__.__subclasses__()")
    assert "Prohibited dunder attribute access: __subclasses__" in str(exc_info.value)

def test_guard_strict_allowlist_mode():
    strict_policy = {
        "version": "1.0",
        "strict_allowlist_mode": True,
        "allowed_modules": ["math"],
        "prohibited_modules": []
    }
    configure_policy(policy_data=strict_policy)

    @guard
    def guarded_runner(code: str):
        return "EXECUTED"

    with pytest.raises(PermissionError) as exc_info:
        guarded_runner("import json")
    assert "Strict allowlist violation: module 'json' not permitted" in str(exc_info.value)

    assert guarded_runner("import math") == "EXECUTED"

def test_guard_async_coroutine_dispatch():
    async def _run():
        @guard
        async def async_agent_tool(payload: dict) -> dict:
            return {"status": "ok", "processed": True}

        safe_call = await async_agent_tool({"arguments": "answer = 42"})
        assert safe_call["status"] == "ok"

        with pytest.raises(PermissionError):
            await async_agent_tool({"arguments": "import os; os.system('echo pwned')"})

    asyncio.run(_run())
