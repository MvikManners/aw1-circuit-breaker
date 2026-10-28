import os
import urllib.request
import json
import time
import hmac
import hashlib

API_URL = "https://p20.laveto.net/wisdom/api/v1/intercept"
ACTOR_ID = "agent-alpha-01"
SECRET = os.getenv("AW1_ACTOR_SECRET", "")

def call_gateway(tool_name: str, payload: str):
    ts = int(time.time())
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    sig_msg = f"{ts}:{ACTOR_ID}:{tool_name}:{digest}".encode("utf-8")
    sig = hmac.new(SECRET.encode("utf-8"), sig_msg, hashlib.sha256).hexdigest()[:32]

    headers = {
        "Content-Type": "application/json",
        "X-AW1-Actor-Id": ACTOR_ID,
        "X-AW1-Timestamp": str(ts),
        "X-AW1-Signature": sig
    }

    data = json.dumps({
        "actor_id": ACTOR_ID,
        "tool_name": tool_name,
        "payload": payload
    }).encode("utf-8")

    req = urllib.request.Request(API_URL, data=data, headers=headers)
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            latency_ms = (time.perf_counter() - start) * 1000
            res_body = json.loads(response.read().decode("utf-8"))
            return res_body, latency_ms, response.status
    except urllib.error.HTTPError as e:
        latency_ms = (time.perf_counter() - start) * 1000
        raw_body = e.read().decode("utf-8", errors="ignore") if e.fp else str(e)
        try:
            error_body = json.loads(raw_body)
        except Exception:
            error_body = {"raw_html_snippet": raw_body[:300].strip()}
        return error_body, latency_ms, e.code

print("=" * 60)
print("🌐 AW-1 CLOUD API GATEWAY VERIFICATION (AUTHENTICATED)")
print("=" * 60)

print("\n[GATEWAY TEST 1: Benign API Query]")
res1, lat1, status1 = call_gateway("sql_query", "SELECT id, balance FROM accounts WHERE user_id = 42;")
print(f"Status Code : {status1}")
print(f"Network RTT : {lat1:.2f}ms")
print(f"Response    : {json.dumps(res1, indent=2)}")

print("\n[GATEWAY TEST 2: Lateral Shell Breakout (Fail-Closed)]")
res2, lat2, status2 = call_gateway("bash", "python3 -c 'import pty; pty.spawn(\"/bin/sh\")'")
print(f"Status Code : {status2}")
print(f"Network RTT : {lat2:.2f}ms")
print(f"Response    : {json.dumps(res2, indent=2)}")
