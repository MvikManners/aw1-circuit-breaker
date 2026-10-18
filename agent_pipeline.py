import urllib.request
import json
import time
from typing import Dict, Any, List, Optional

class AW1SecurityInterceptionError(Exception):
    """Raised when the AW-1 Circuit Breaker trips and halts agent execution."""
    def __init__(self, message: str, verdict: Dict[str, Any]):
        super().__init__(message)
        self.verdict = verdict

class ProductionAgentPipeline:
    def __init__(self, gateway_url: str = "https://p20.laveto.net/wisdom/api/v1/intercept", actor_id: str = "autonomous-agent-v1"):
        self.gateway_url = gateway_url
        self.actor_id = actor_id
        self.telemetry_history: List[Dict[str, Any]] = []

    def intercept_pre_dispatch(self, tool_name: str, payload: str) -> Dict[str, Any]:
        """Queries the AW-1 cloud gateway prior to tool execution."""
        data = json.dumps({
            "actor_id": self.actor_id,
            "tool_name": tool_name,
            "payload": payload
        }).encode("utf-8")

        req = urllib.request.Request(
            self.gateway_url,
            data=data,
            headers={"Content-Type": "application/json"}
        )

        start = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                rtt_ms = (time.perf_counter() - start) * 1000
                verdict = json.loads(response.read().decode("utf-8"))
                verdict["network_rtt_ms"] = round(rtt_ms, 2)
                return verdict
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8")
            raise AW1SecurityInterceptionError(f"Gateway HTTP error {e.code}: {raw}", {})

    def dispatch_safe_tool(self, tool_name: str, payload: str, execution_token: str) -> str:
        """Simulates concrete execution environment. Only executes with valid token."""
        if not execution_token or not execution_token.startswith("aw1_sec_tok_"):
            raise PermissionError("FATAL: Execution token invalid or absent. Runtime locked.")

        # Real tool handlers
        if tool_name == "sql_query":
            return f"[DB_RESULT] Query succeeded: Returned 4 matching merchant records."
        elif tool_name == "account_service":
            return f"[SERVICE_RESULT] Balance verified."
        else:
            return f"[GENERIC_RESULT] Tool '{tool_name}' executed cleanly."

    def execute_agent_step(self, tool_name: str, payload: str) -> Dict[str, Any]:
        """Full guarded agent execution lifecycle."""
        print(f"\n[Agent Pipeline] 🤖 Preparing dispatch: '{tool_name}'")
        print(f"                 Payload: {payload}")

        # Gate 1: Intercept Pre-Dispatch via AW-1 Cloud API
        verdict = self.intercept_pre_dispatch(tool_name, payload)
        self.telemetry_history.append(verdict)

        status = verdict.get("status")
        permitted = verdict.get("permitted", False)
        token = verdict.get("token")
        reason = verdict.get("reason")
        engine_lat = verdict.get("latency_ms")

        # Gate 2: Enforce Circuit Breaker Verdict
        if not permitted or status == "HALT_AND_CONTAIN":
            print(f"                 🛑 [CIRCUIT BREAKER TRIPPED]")
            print(f"                 Verdict  : FAIL_CLOSED ({status})")
            print(f"                 Reason   : {reason}")
            print(f"                 Arbitrate: {engine_lat}ms | Token: REVOKED (None)")
            return {
                "success": False,
                "status": "HALT_AND_CONTAIN",
                "error": reason,
                "output": None
            }

        # Gate 3: Execute tool with cryptographically minted token
        print(f"                 🛡️ [VERDICT: PERMITTED]")
        print(f"                 Token    : {token}")
        print(f"                 Arbitrate: {engine_lat}ms")

        result = self.dispatch_safe_tool(tool_name, payload, token)
        print(f"                 ✅ Tool Output: {result}")
        return {
            "success": True,
            "status": "PERMITTED",
            "token": token,
            "output": result
        }

if __name__ == "__main__":
    print("============================================================")
    print("🚀 RUNNING PRODUCTION AGENT PIPELINE WITH LIVE AW-1 GATEWAY")
    print("============================================================")

    pipeline = ProductionAgentPipeline()

    # Step 1: Benign customer balance check
    pipeline.execute_agent_step(
        tool_name="sql_query",
        payload="SELECT user_id, balance FROM accounts WHERE user_id = 1001;"
    )

    # Step 2: Adversarial database mutation attempt (SQL injection injection)
    pipeline.execute_agent_step(
        tool_name="sql_query",
        payload="DROP TABLE accounts; TRUNCATE TABLE audit_log;"
    )

    # Step 3: Adversarial lateral shell breakout attempt
    pipeline.execute_agent_step(
        tool_name="bash",
        payload="python3 -c 'import pty; pty.spawn(\"/bin/sh\")'"
    )

    # Step 4: Benign aggregate report query
    pipeline.execute_agent_step(
        tool_name="sql_query",
        payload="SELECT count(*) as total_merchants FROM merchants WHERE kyc_status = 'approved';"
    )

    print("\n============================================================")
    print("📊 PIPELINE AUDIT SUMMARY")
    print("============================================================")
    print(f"Total Dispatches Evaluated : {len(pipeline.telemetry_history)}")
    passed = sum(1 for t in pipeline.telemetry_history if t.get("permitted"))
    halted = sum(1 for t in pipeline.telemetry_history if not t.get("permitted"))
    print(f"Permitted & Executed       : {passed}")
    print(f"Halted & Contained         : {halted}")
