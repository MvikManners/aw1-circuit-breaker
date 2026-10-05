import requests
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://p20.laveto.net/wisdom/api/v1/aw/pouc/submit"

NODES = [
    {
        "node_id": "edge_node_bw_gaborone_002",
        "region": "Gaborone Innovation Hub",
        "blindspot": "SEZA Sir Seretse Khama freight cargo scanning turnaround delay patterns identified in cold-chain logistics."
    },
    {
        "node_id": "edge_node_bw_francistown_003",
        "region": "Francistown Logistics Core",
        "blindspot": "CEDA northern agro-processing distribution route inefficiencies between Francistown and Nata junctions."
    },
    {
        "node_id": "edge_node_bw_kasane_004",
        "region": "Kasane Kazungula Corridor",
        "blindspot": "Kazungula One-Stop Border Post inter-modal weighbridge transit queues causing customs clearing latency."
    },
    {
        "node_id": "edge_node_bw_maun_005",
        "region": "Maun Delta Operations",
        "blindspot": "Eco-tourism aviation fuel supply chain monitoring discrepancies detected across seasonal dry spells."
    }
]

def submit_task(node_cfg, run_id):
    ref_id = f"TXN_{node_cfg['node_id'].upper()}_{run_id}_{int(time.time()*1000)}"
    payload = {
        "node_id": node_cfg["node_id"],
        "telemetry": {
            "power_source": "AC_CHARGING",
            "network_type": "UNMETERED_WIFI",
            "battery_level_percent": 96,
            "thermal_state_celsius": 29.5
        },
        "scores": {
            "comprehension": 0.94,
            "integrity": 0.96,
            "practicality": 0.91
        },
        "surfaced_blindspot": node_cfg["blindspot"],
        "peer_scores": [0.93, 0.95],
        "economic_proof": {
            "proof_type": "SEZA_IOT_TELEMETRY_AUDIT",
            "reference_id": ref_id,
            "fiat_amount_bwp": 50.00
        }
    }

    t0 = time.time()
    try:
        res = requests.post(BASE_URL, json=payload, timeout=20.0)
        dt = round(time.time() - t0, 3)
        return {
            "node_id": node_cfg["node_id"],
            "status_code": res.status_code,
            "time_sec": dt,
            "data": res.json() if res.status_code == 200 else res.text,
            "ref_id": ref_id
        }
    except Exception as e:
        return {
            "node_id": node_cfg["node_id"],
            "status_code": 500,
            "time_sec": round(time.time() - t0, 3),
            "error": str(e),
            "ref_id": ref_id
        }

def run_simulation(total_runs=4):
    print("=" * 65)
    print("LAVETO AW-1 CONCURRENT EDGE NODE SIMULATOR")
    print(f"Target: {BASE_URL}")
    print(f"Simulating {len(NODES)} distinct nodes across {total_runs} concurrent batches...")
    print("=" * 65)

    tasks = []
    run_id = uuid.uuid4().hex[:6]

    with ThreadPoolExecutor(max_workers=len(NODES)) as executor:
        for node in NODES:
            tasks.append(executor.submit(submit_task, node, run_id))

        results = [t.result() for t in as_completed(tasks)]

    all_passed = True
    print("\nBatch Ingestion Results:")
    for r in results:
        code = r["status_code"]
        node = r["node_id"]
        sec = r["time_sec"]
        if code == 200:
            receipt = r["data"].get("settlement_receipt", {})
            minted = receipt.get("awt_minted", 0.0)
            w_tau = receipt.get("w_tau_credited", 0.0)
            print(f"  ✓ [{node}] HTTP 200 ({sec}s) -> Minted: +{minted} AWT, Credited: +{w_tau} W_tau")
        else:
            all_passed = False
            print(f"  ✗ [{node}] HTTP {code} ({sec}s) -> {r.get('data') or r.get('error')}")

    print("\n" + "=" * 65)
    if all_passed:
        print("SIMULATION SUCCESS: All distributed edge nodes settled concurrently.")
    else:
        print("SIMULATION WARNING: Concurrency bottlenecks or lock issues detected.")
    print("=" * 65)

if __name__ == "__main__":
    run_simulation()
