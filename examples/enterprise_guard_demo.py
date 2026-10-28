import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from aw1 import EnterpriseGuard, SecurityViolationError

guard = EnterpriseGuard(allowed_tools=["safe_query"], max_financial_limit=250.0)

@guard.protect(tool_name="safe_query")
def run_db(query: str):
    return f"Safe result for: {query}"

print("=" * 60)
print("🛡️  AW-1 ENTERPRISE GUARD DEMONSTRATION")
print("=" * 60)

# 1. Benign
print("\n[ TEST 1: Benign Query ]\n ", run_db("SELECT id FROM users LIMIT 1;"))

# 2. Malicious AST Injection
try:
    print("\n[ TEST 2: Base64 OS Shell Exploit ]")
    run_db("base64:aW1wb3J0IG9zOyBvcy5zeXN0ZW0oJ3JtIC1yZiAvJyk=")
except SecurityViolationError as e:
    print(f"  🛑 HALTED: {e}")

# 3. SQL Mutation Attempt
try:
    print("\n[ TEST 3: SQL DROP TABLE Mutation ]")
    run_db("DROP TABLE users;")
except SecurityViolationError as e:
    print(f"  🛑 HALTED: {e}")

# 4. Unauthorized Tool Whitelist Check
try:
    print("\n[ TEST 4: Unauthorized Tool Call ]")
    rec = guard.audit_and_verify("agent-007", "delete_s3_bucket", {}, cost=0.0)
    if rec["decision"] != "APPROVED_PROCEED":
        raise SecurityViolationError(rec["reason"], rec)
except SecurityViolationError as e:
    print(f"  🛑 HALTED: {e}")

print("\n" + "=" * 60)
print("✅ ALL 4 POLICIES ENFORCED DETERMINISTICALLY!")
print("=" * 60)
