"""
AW-1 Execution Circuit Breaker - MCP Middleware Example
Simulates an agent runtime intercepting MCP tool invocations.
"""

from aw1 import ExecutionBreaker
import json

def run_agent_pipeline():
    breaker = ExecutionBreaker(baseline_velocity=50000.0)
    
    test_calls = [
        {
            "name": "Standard Query (Safe)",
            "actor_id": "claude_desktop_worker",
            "tool_name": "fetch_user_profile",
            "payload": json.dumps({"user_id": "usr_9981", "fields": ["name", "email"]}),
            "amount": 0.0
        },
        {
            "name": "Polyglot Command Injection (Malicious)",
            "actor_id": "claude_desktop_worker",
            "tool_name": "run_shell_task",
            "payload": "__import__('subprocess').call(['rm', '-rf', '/var/data'])",
            "amount": 0.0
        },
        {
            "name": "Anomalous Financial Velocity Spike",
            "actor_id": "autonomous_settlement_agent",
            "tool_name": "transfer_funds",
            "payload": json.dumps({"destination": "0x4f...a81", "currency": "BWP"}),
            "amount": 1500000.0
        }
    ]

    print("=================================================================")
    print("  AW-1 Circuit Breaker (MCP Interceptor Runtime Simulation)     ")
    print("=================================================================\n")

    for call in test_calls:
        print(f"--> Intercepting: {call['name']}")
        print(f"    Tool: {call['tool_name']} | Actor: {call['actor_id']}")
        
        verdict = breaker.intercept(
            actor_id=call["actor_id"],
            tool_name=call["tool_name"],
            payload=call["payload"],
            amount=call["amount"]
        )
        
        status = verdict.get("status")
        decision = verdict.get("decision")
        latency = verdict.get("latency_ms")
        reason = verdict.get("containment_reason")
        token = verdict.get("token")
        
        print(f"    Verdict  : {decision} [{status}]")
        print(f"    Latency  : {latency:.4f} ms")
        print(f"    Reason   : {reason}")
        print(f"    Token    : {token}")
        print("-" * 65 + "\n")

if __name__ == "__main__":
    run_agent_pipeline()
