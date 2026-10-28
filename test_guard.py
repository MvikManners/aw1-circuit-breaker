from aw1 import EnterpriseGuard, SecurityViolationError

# Configure boundaries
guard = EnterpriseGuard(
    allowed_tools=["db_query"],
    readonly_sql=True
)

@guard.protect(tool_name="db_query")
def run_query(query: str):
    return f"Executed: {query}"

# Test 1: Safe read query
print("--- Test 1: Safe Query ---")
print(run_query("SELECT id, name FROM users;"))

# Test 2: Dangerous drop query
print("\n--- Test 2: Malicious Query ---")
try:
    print(run_query("DROP TABLE users;"))
except SecurityViolationError as err:
    print(f"🛑 Blocked by Guard: {err}")
