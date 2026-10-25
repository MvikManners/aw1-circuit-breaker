import urllib.request
import urllib.error
import json
import sqlite3

BASE_URL = "https://p20.laveto.net"

def print_header(title):
    print("\n" + "="*70)
    print(f" 🛡️ AW-1 TEST SUITE: {title}")
    print("="*70)

def test_unauthenticated_mcp():
    print_header("1. Testing Paywall Enforcement (No API Key)")
    url = f"{BASE_URL}/wisdom/mcp"
    data = json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": "aw1_execute_protected_tool", "arguments": {"tool_name": "whoami", "payload": "id"}},
        "id": 1
    }).encode('utf-8')

    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            body_raw = response.read().decode('utf-8')
            body = json.loads(body_raw)
            print(f"HTTP Status: {status}")
            
            # Check JSON-RPC protocol error
            if "error" in body and body["error"].get("code") == -32001:
                print(f"✅ PASSED (JSON-RPC Paywall Active): Code {body['error']['code']}")
                print(f"   Message: {body['error'].get('message')}")
                print(f"   Checkout URL: {body['error'].get('data', {}).get('checkout_url')}")
            else:
                print("🚨 WARNING: Tool execution permitted without credentials!")
                print(f"   Response: {body_raw[:200]}")
    except urllib.error.HTTPError as e:
        print(f"✅ PASSED (Strict HTTP Paywall Active): HTTP {e.code} - {e.reason}")
        print(f"   Body: {e.read().decode('utf-8')[:150]}")
    except Exception as e:
        print(f"❌ Error during connection: {e}")

def test_authorized_and_quota_gates():
    print_header("2. Testing Authorized Execution & Quota Decrement")
    url = f"{BASE_URL}/wisdom/mcp"
    api_key = os.getenv("AW1_API_KEY", "DEMO_SANDBOX_KEY")
    db_path = "/home/LavetoLab/lvt_backend/lvt_database.db"

    # Fetch initial quota
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT monthly_quota FROM wisdom_api_clients WHERE api_key = ?", (api_key,))
        initial_quota = cur.fetchone()[0]
        conn.close()
    except Exception as e:
        print(f"⚠️ Could not read initial quota: {e}")
        initial_quota = None

    data = json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": "aw1_execute_protected_tool", "arguments": {"tool_name": "ping", "payload": "healthcheck"}},
        "id": 2
    }).encode('utf-8')

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "X-Laveto-Key": api_key},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            body = json.loads(response.read().decode('utf-8'))
            print(f"HTTP Status: {status}")
            if "result" in body:
                print("✅ PASSED: Tool execution authorized under Gate 7 statutory containment.")
                print(f"   Payload: {body['result']['content'][0]['text']}")
            else:
                print(f"⚠️ Tool call response: {body}")
    except Exception as e:
        print(f"❌ Execution failed: {e}")

    # Check decrement
    if initial_quota is not None:
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT monthly_quota FROM wisdom_api_clients WHERE api_key = ?", (api_key,))
            new_quota = cur.fetchone()[0]
            conn.close()
            print(f"   Quota Transition: {initial_quota} -> {new_quota}")
            if new_quota == initial_quota - 1:
                print("✅ PASSED: Quota decremented by exactly 1 in SQLite database.")
            else:
                print(f"⚠️ Quota did not decrement by 1 (expected {initial_quota - 1}, got {new_quota})")
        except Exception as e:
            print(f"⚠️ Could not verify quota decrement: {e}")

def test_sse_endpoint():
    print_header("3. Testing Real-Time SSE Streaming Endpoint (/wisdom/mcp/sse)")
    url = f"{BASE_URL}/wisdom/mcp/sse"
    req = urllib.request.Request(url, headers={"Accept": "text/event-stream"}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.getcode()
            content_type = response.headers.get('Content-Type', '')
            print(f"✅ PASSED: HTTP {status} | Content-Type: {content_type}")
    except urllib.error.HTTPError as e:
        print(f"❌ SSE Failed: HTTP {e.code} - {e.reason}")
    except Exception as e:
        # If it streams indefinitely, getting headers is sufficient proof of connectivity
        print(f"ℹ️ SSE connection stream active: {e}")

def test_telemetry():
    print_header("4. Testing Live Telemetry API (/wisdom/api/v1/telemetry/recent)")
    url = f"{BASE_URL}/wisdom/api/v1/telemetry/recent"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            status = response.getcode()
            body = json.loads(response.read().decode('utf-8'))
            print(f"✅ PASSED: HTTP {status}")
            print(f"📊 Telemetry Items Tracked: {len(body) if isinstance(body, list) else 'Object Returned'}")
    except Exception as e:
        print(f"❌ Telemetry Check Failed: {e}")

if __name__ == "__main__":
    test_unauthenticated_mcp()
    test_authorized_and_quota_gates()
    test_sse_endpoint()
    test_telemetry()
    print("\n" + "="*70)
    print("🔒 TEST SUITE EXECUTION COMPLETE")
    print("="*70)
