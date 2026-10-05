import requests
import time

BASE_URL = "https://p20.laveto.net/wisdom/api/v1/aw/pouc/submit"

def test_pipeline():
    print("=" * 60)
    print("RUNNING LAVETO AW-1 CIRCUIT BREAKER REGRESSION SUITE")
    print("=" * 60)

    # Gate 1: Hardware Rejection
    print("\n[Gate 1] Testing Hardware Interlock Rejection...")
    r1 = requests.post(BASE_URL, json={
        "node_id": "rogue_hw_node",
        "telemetry": {"power_source": "BATTERY", "network_type": "cellular", "battery_level_percent": 45, "thermal_state_celsius": 40.0},
        "scores": {"comprehension": 0.5, "integrity": 0.5, "practicality": 0.5},
        "surfaced_blindspot": "Standard diagnostic execution.",
        "peer_scores": [0.5, 0.5]
    })
    assert r1.status_code == 422, f"Failed Gate 1: expected 422, got {r1.status_code}"
    print("  ✓ PASS: Rejected rogue hardware constraints (HTTP 422).")

    # Gate 2: Semantic Novelty Gate
    print("\n[Gate 2] Testing Semantic Novelty Gate...")
    r2 = requests.post(BASE_URL, json={
        "node_id": "boilerplate_bot",
        "telemetry": {"power_source": "AC_CHARGING", "network_type": "UNMETERED_WIFI", "battery_level_percent": 90, "thermal_state_celsius": 31.0},
        "scores": {"comprehension": 0.8, "integrity": 0.8, "practicality": 0.8},
        "surfaced_blindspot": "Proceed with standard execution without additional evaluation.",
        "peer_scores": [0.8, 0.8]
    })
    assert r2.status_code == 400, f"Failed Gate 2: expected 400, got {r2.status_code}"
    print("  ✓ PASS: Rejected synthetic boilerplate echo (HTTP 400).")

    # Gate 3: Economic Proof Gate
    print("\n[Gate 3] Testing Economic Proof Gate...")
    r3 = requests.post(BASE_URL, json={
        "node_id": "unbacked_mining_node",
        "telemetry": {"power_source": "AC_CHARGING", "network_type": "UNMETERED_WIFI", "battery_level_percent": 92, "thermal_state_celsius": 30.5},
        "scores": {"comprehension": 0.9, "integrity": 0.9, "practicality": 0.9},
        "surfaced_blindspot": "SEZA statutory evaluation on Kazungula freight corridors.",
        "peer_scores": [0.88, 0.91]
    })
    assert r3.status_code == 422, f"Failed Gate 3: expected 422, got {r3.status_code}"
    print("  ✓ PASS: Rejected unbacked mint attempt without institutional proof (HTTP 422).")

    # Gate 4: Golden Path Settlement & Persistence
    print("\n[Gate 4] Testing Golden Path Settlement & Persistence...")
    batch_ref = f"TXN_SEZA_REGRESSION_{int(time.time())}"
    payload = {
        "node_id": "edge_node_bw_001",
        "telemetry": {"power_source": "AC_CHARGING", "network_type": "UNMETERED_WIFI", "battery_level_percent": 95, "thermal_state_celsius": 30.0},
        "scores": {"comprehension": 0.95, "integrity": 0.95, "practicality": 0.92},
        "surfaced_blindspot": "SEZA multi-modal transport dispatch bottlenecks identified near Kazungula junction affecting grain trade corridors.",
        "peer_scores": [0.92, 0.94],
        "economic_proof": {
            "proof_type": "SEZA_IOT_TELEMETRY_AUDIT",
            "reference_id": batch_ref,
            "fiat_amount_bwp": 50.00
        }
    }
    r4 = requests.post(BASE_URL, json=payload)
    assert r4.status_code == 200, f"Failed Gate 4: expected 200, got {r4.status_code} - {r4.text}"
    receipt = r4.json()["settlement_receipt"]
    print(f"  ✓ PASS: Validated & settled (+{receipt['awt_minted']} AWT, +{receipt['w_tau_credited']} W_tau).")

    # Gate 5: Replay Attack / Idempotency Rejection
    print("\n[Gate 5] Testing Idempotency & Replay Protection...")
    r5 = requests.post(BASE_URL, json=payload)
    assert r5.status_code in (409, 422), f"Failed Gate 5: expected 409/422 on replay, got {r5.status_code}"
    print(f"  ✓ PASS: Replay rejected with HTTP {r5.status_code}.")

    print("\nALL CIRCUIT BREAKER GATES OPERATIONAL.")

if __name__ == "__main__":
    test_pipeline()
