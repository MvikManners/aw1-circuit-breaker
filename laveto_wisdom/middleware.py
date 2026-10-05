import functools
import json
from laveto_wisdom.breaker import ExecutionBreaker, SecurityTripwireException

def protect_tool(license_key: str = None, breaker_instance: ExecutionBreaker = None, 
                 cost_bwp: float = 0.0, agent_id: str = "agent_planner", 
                 attestations: list = None, quorum_threshold: int = 2):
    """
    1-Line Universal Decorator to wrap any Python function or Agent Tool 
    with the 5-Tier AW-1 Sovereign Circuit Breaker.
    """
    active_breaker = breaker_instance or ExecutionBreaker(
        license_key=license_key or "AW1-DEFAULT-KEY", 
        enable_canary=True
    )

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tool_name = func.__name__
            # Serialize payload arguments for AST & Statutory inspection
            payload_str = f"{tool_name}(args={repr(args)}, kwargs={repr(kwargs)})"
            
            result = active_breaker.execute_tool(
                tool_name=tool_name,
                payload=payload_str,
                agent_id=agent_id,
                cost_bwp=cost_bwp,
                attestations=attestations,
                quorum_threshold=quorum_threshold
            )
            
            # If the breaker trips and Canary generates a decoy output, return decoy
            if result.get("execution_status") == "SUCCESS" and result.get("security_audit", {}).get("circuit_breaker") == "TRIPPED_CANARY":
                return result["output"]
            
            # If blocked by Statutory Lens or Quorum
            if result.get("execution_status") == "BLOCKED":
                raise SecurityTripwireException(result["output"])
            
            # Otherwise execute the real underlying function
            return func(*args, **kwargs)
        return wrapper
    return decorator


class LangChainAW1Callback:
    """
    Middleware Callback Handler for LangChain and LangGraph Agent Tool Execution.
    """
    def __init__(self, license_key: str, agent_id: str = "langchain_agent"):
        self.breaker = ExecutionBreaker(license_key=license_key, enable_canary=True)
        self.agent_id = agent_id

    def on_tool_start(self, serialized: dict, input_str: str, **kwargs):
        tool_name = serialized.get("name", "unknown_tool")
        res = self.breaker.execute_tool(
            tool_name=tool_name,
            payload=input_str,
            agent_id=self.agent_id
        )
        if res.get("execution_status") == "BLOCKED":
            raise SecurityTripwireException(res["output"])
        return res
