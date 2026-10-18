import time
import json
import urllib.request
import os

TELEMETRY_URL = "https://p20.laveto.net/wisdom/api/v1/telemetry/recent"
SEEN_EVENTS_CACHE = "/home/LavetoLab/.aw1_alerted_events.json"

def load_seen_events() -> set:
    if os.path.exists(SEEN_EVENTS_CACHE):
        try:
            with open(SEEN_EVENTS_CACHE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_seen_events(seen: set):
    with open(SEEN_EVENTS_CACHE, "w") as f:
        json.dump(list(seen)[-200:], f)

def dispatch_incident_alert(event: dict):
    """
    Dispatches immediate alert when an agent triggers Gate containment.
    Can be hooked into Slack, Discord, PagerDuty, or webhook dispatcher.
    """
    evt_id = event.get("id")
    actor = event.get("actor")
    tool = event.get("tool")
    reason = event.get("reason")
    ts = event.get("timestamp")
    prev_hash = event.get("prev_hash", "")[:12]
    rec_hash = event.get("record_hash", "")[:12]

    alert_box = (
        f"🚨 [AW-1 SECURITY CONTAINMENT INCIDENT] 🚨\n"
        f"Event ID    : {evt_id}\n"
        f"Timestamp   : {ts}\n"
        f"Actor       : {actor}\n"
        f"Tool Blocked: {tool}\n"
        f"Containment : {reason}\n"
        f"Audit Hash  : {prev_hash}... -> {rec_hash}...\n"
        f"Status      : FAIL_CLOSED (Execution Thwarted)"
    )
    print(alert_box)

def poll_telemetry_ledger():
    seen_events = load_seen_events()
    try:
        req = urllib.request.Request(TELEMETRY_URL, headers={"User-Agent": "AW1-Sentinel/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            events = data.get("events", [])
            
            new_alerts = 0
            for evt in events:
                evt_id = evt.get("id")
                if evt_id not in seen_events:
                    seen_events.add(evt_id)
                    if evt.get("status") in ("HALT_AND_CONTAIN", "FAIL_CLOSED") or not evt.get("permitted"):
                        dispatch_incident_alert(evt)
                        new_alerts += 1
            
            save_seen_events(seen_events)
            if new_alerts == 0:
                print(f"✅ Sentinel audit complete: All {len(events)} recent events evaluated. No unhandled breach alerts.")
    except Exception as e:
        print(f"⚠️ Telemetry polling failure: {e}")

if __name__ == "__main__":
    poll_telemetry_ledger()
