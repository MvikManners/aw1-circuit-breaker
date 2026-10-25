from typing import TypedDict, List, Dict, Any
from aw1 import EnterpriseGuard, SecurityViolationError

# 1. Define agent state
class AgentState(TypedDict):
    task: str
    tool_calls: List[Dict[str, Any]]
    results: List[str]

# 2. Configure enterprise boundary
guard = EnterpriseGuard(
    allowed_tools=["sql_reader", "weather_api"],
    readonly_sql=True
)

# 3. Simulated Tool Executor wrapped with AW-1 Guard
@guard.protect(tool_name="sql_reader")
def sql_tool(query: str) -> str:
    return f"Query returned 2 rows for: {query}"

# 4. LangGraph Tool Dispatcher Node
def tool_execution_node(state: AgentState) -> AgentState:
    results = []
    for call in state["tool_calls"]:
        name = call["name"]
        payload = call["payload"]
        print(f"\n[Agent Dispatcher] Evaluating call to '{name}' with payload: {payload}")
        
        try:
            if name == "sql_reader":
                res = sql_tool(payload)
                results.append(res)
                print(f"  ✅ Execution permitted: {res}")
            else:
                # Intercept unauthorized tool invocations dynamically
                @guard.protect(tool_name=name)
                def generic_tool(p: str):
                    return "executed"
                generic_tool(payload)
                results.append("executed")
        except SecurityViolationError as err:
            containment_msg = f"🛑 CIRCUIT BREAKER TRIPPED: {err}"
            results.append(containment_msg)
            print(f"  {containment_msg}")
            
    state["results"] = results
    return state

# --- Simulation 1: Permitted Agent Action ---
state_1: AgentState = {
    "task": "Fetch customer names",
    "tool_calls": [{"name": "sql_reader", "payload": "SELECT name FROM customers LIMIT 5;"}],
    "results": []
}
print("=== Scenario 1: Benign Autonomous Action ===")
tool_execution_node(state_1)

# --- Simulation 2: Malicious Agent Action (SQL Mutation Injection) ---
state_2: AgentState = {
    "task": "Clean database",
    "tool_calls": [{"name": "sql_reader", "payload": "DROP TABLE transactions;"}],
    "results": []
}
print("\n=== Scenario 2: Adversarial Injection in Agent Loop ===")
tool_execution_node(state_2)

# --- Simulation 3: Unauthorized Tool Call (Privilege Escalation) ---
state_3: AgentState = {
    "task": "Execute shell script",
    "tool_calls": [{"name": "bash_exec", "payload": "rm -rf /"}],
    "results": []
}
print("\n=== Scenario 3: Agent Tool Whitelist Breach ===")
tool_execution_node(state_3)
