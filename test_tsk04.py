import json
from aw1_hcs_worker import HederaHCSClient

with open("/home/LavetoLab/aw1-breaker/hcs_config.json") as f:
    cfg = json.load(f)

with open("/home/LavetoLab/aw1-breaker/db_config.json") as f:
    db_cfg = json.load(f)

client = HederaHCSClient(cfg, db_cfg=db_cfg)

test_payload = {
    "dossier_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "audit_id": 9999
}

res1 = client.submit_attestation(test_payload)
res2 = client.submit_attestation(test_payload)

print("=== VERIFYING SIMULATED SANDBOX ENVELOPE ===")
print(f"Sequence 1: {res1['sequence_number']}")
print(f"Sequence 2: {res2['sequence_number']}")
print(f"Tx ID:      {res1['tx_id']}")
print(f"Topic ID:   {client.topic_id}")
print(f"Mode:       {res1.get('mode')}")

assert res2["sequence_number"] == res1["sequence_number"] + 1, "Monotonic sequence check failed!"
assert not res1["tx_id"].startswith("0.0.0.0."), "Double prefix detected!"
assert "YOUR_TOPIC_ID" not in client.topic_id, "Placeholder topic ID detected!"
assert "YOUR_ACCOUNT_ID" not in res1["tx_id"], "Placeholder account ID detected!"
assert res1.get("mode") == "SIMULATED_SANDBOX", "Missing SIMULATED_SANDBOX mode tag!"

print("\n[✓] ALL TSK-04 CHECKS PASSED: Sandbox sanitized, monotonic, and segregated.")
