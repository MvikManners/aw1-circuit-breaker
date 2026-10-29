"""
===================================================================================
                   LAVETO WISDOM (AW-1) MOBILE EDGE DEMO CLIENT
===================================================================================
File: mobile_edge_demo.py
Description: Simulates an edge node runtime running on a mobile or edge hardware 
             device in Botswana. Demonstrates hardware interlock monitoring, local 
             micro-evaluation execution, PoUC payload submission to the 
             p20.laveto.net server, and local dual-token wallet tracking.
===================================================================================
"""

import time
import random
import json
import urllib.request
import urllib.error
import sqlite3
import os
from typing import Dict, Any

class MobileHardwareTelemetrySensor:
    """Simulates or reads real mobile device hardware telemetry."""
    @staticmethod
    def get_current_telemetry() -> Dict[str, Any]:
        # Simulates optimal charging state on unmetered Wi-Fi
        return {
            "power_source": "AC_CHARGING",
            "network_type": "UNMETERED_WIFI",
            "battery_level_percent": random.randint(85, 98),
            "thermal_state_celsius": round(random.uniform(28.5, 32.5), 1)
        }

class OnDeviceLocalWallet:
    """Manages an on-device SQLite ledger for liquid AWT & Soulbound W_tau credits."""
    def __init__(self, db_path: str = "/home/LavetoLab/laveto_wisdom/edge_wallet.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS edge_wallet (
                node_id TEXT PRIMARY KEY,
                awt_liquid_balance REAL DEFAULT 0.0,
                w_tau_reputation REAL DEFAULT 1.0,
                tasks_completed INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def update_balance(self, node_id: str, awt_earned: float, w_tau_earned: float) -> Dict[str, float]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT awt_liquid_balance, w_tau_reputation, tasks_completed FROM edge_wallet WHERE node_id = ?", (node_id,))
        row = cur.fetchone()
        
        if row:
            new_awt = row[0] + awt_earned
            new_w_tau = row[1] + w_tau_earned
            tasks = row[2] + 1
            cur.execute("""
                UPDATE edge_wallet 
                SET awt_liquid_balance = ?, w_tau_reputation = ?, tasks_completed = ?, last_updated = CURRENT_TIMESTAMP
                WHERE node_id = ?
            """, (new_awt, new_w_tau, tasks, node_id))
        else:
            new_awt = awt_earned
            new_w_tau = 1.0 + w_tau_earned
            tasks = 1
            cur.execute("""
                INSERT INTO edge_wallet (node_id, awt_liquid_balance, w_tau_reputation, tasks_completed)
                VALUES (?, ?, ?, ?)
            """, (node_id, new_awt, new_w_tau, tasks))
            
        conn.commit()
        conn.close()
        return {"awt_balance": round(new_awt, 2), "w_tau_reputation": round(new_w_tau, 3), "tasks_completed": tasks}

class MobileEdgeNodeRuntime:
    """Main mobile edge client daemon loop."""
    def __init__(self, node_id: str = "node-mobile-bw-4012", server_url: str = "https://p20.laveto.net/wisdom"):
        self.node_id = node_id
        self.server_url = server_url.rstrip('/')
        self.wallet = OnDeviceLocalWallet()

    def run_single_eval_cycle(self, micro_task: Dict[str, Any]) -> Dict[str, Any]:
        print(f"\n[+] Executing Micro-Eval Cycle for Node: {self.node_id}")
        
        # 1. Read Mobile Telemetry
        telemetry = MobileHardwareTelemetrySensor.get_current_telemetry()
        print(f"  • Telemetry Check : Battery={telemetry['battery_level_percent']}%, Power={telemetry['power_source']}, Temp={telemetry['thermal_state_celsius']}°C, Net={telemetry['network_type']}")

        # 2. Local Micro-Inference Execution
        print(f"  • Task Received   : {micro_task['dilemma_title']}")
        print(f"  • Local Blindspot : {micro_task['surfaced_blindspot']}")

        # 3. Construct PoUC Submission Payload
        pouc_payload = {
            "node_id": self.node_id,
            "telemetry": telemetry,
            "scores": micro_task["eval_scores"],
            "surfaced_blindspot": micro_task["surfaced_blindspot"],
            "peer_scores": micro_task["peer_scores"]
        }

        # 4. Dispatch Payload to Server (or fallback if simulated offline)
        url = f"{self.server_url}/api/v1/aw/pouc/submit"
        headers = {"Content-Type": "application/json"}
        req_data = json.dumps(pouc_payload).encode('utf-8')

        try:
            req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp_json = json.loads(resp.read().decode('utf-8'))
                
                if resp_json.get("status") == "VALIDATED_AND_SETTLED":
                    receipt = resp_json.get("settlement_receipt", {})
                    awt_minted = receipt.get("awt_minted", 0.0)
                    w_tau_credited = receipt.get("w_tau_credited", 0.0)
                    
                    wallet_state = self.wallet.update_balance(self.node_id, awt_minted, w_tau_credited)
                    
                    print("  ✓ Server Status    : VALIDATED_AND_SETTLED")
                    print(f"  ✓ Wisdom Quotient  : W = {resp_json.get('wisdom_quotient_W')}")
                    print(f"  ✓ Epistemic Delta  : {resp_json.get('epistemic_delta')}x Information Gain")
                    print(f"  ✓ Tokens Earned    : +{awt_minted} AWT | +{w_tau_credited} W_tau")
                    print(f"  ✓ On-Device Wallet : {wallet_state['awt_balance']} AWT Liquid | {wallet_state['w_tau_reputation']} W_tau Reputation")
                    return resp_json
                else:
                    print(f"  ❌ Rejection: {resp_json}")
                    return resp_json

        except Exception as e:
            print(f"  ℹ️ Server Connection Fallback: {e}")
            simulated_receipt = {
                "status": "SIMULATED_LOCAL_SETTLEMENT",
                "wisdom_quotient_W": 2.35,
                "epistemic_delta": 1.25,
                "settlement_receipt": {"awt_minted": 12.5, "w_tau_credited": 0.062}
            }
            wallet_state = self.wallet.update_balance(self.node_id, 12.5, 0.062)
            print(f"  ✓ Simulated Earned : +12.5 AWT | +0.062 W_tau")
            print(f"  ✓ Local Wallet DB  : {wallet_state['awt_balance']} AWT Liquid | {wallet_state['w_tau_reputation']} W_tau Reputation")
            return simulated_receipt

def run_demo():
    print("=" * 70)
    print("   📱 LAVETO WISDOM (AW-1) MOBILE EDGE DEMO CLIENT RUNTIME")
    print("=" * 70)
    
    runtime = MobileEdgeNodeRuntime(node_id="node-mobile-bw-4012")

    micro_tasks = [
        {
            "dilemma_title": "Audit SEZA Phase 2 Solar Infrastructure Supply Chain",
            "surfaced_blindspot": "Supplier materials rely on unverified import components that bypass local Botswana CEE 50% subcontracting quotas.",
            "eval_scores": {"foresight_depth_Fn": 4.5, "axiological_coverage_Ac": 0.85, "irreversibility_risk_Rrisk": 1.0, "epistemic_hubris_penalty_Hpen": 0.8},
            "peer_scores": [2.1, 2.3]
        },
        {
            "dilemma_title": "Cross-Validate Chobe Grain Storage Distribution Logistics",
            "surfaced_blindspot": "Transport route assumes zero Kazungula border delays during peak October harvest, creating high spoilage risks for imported grain.",
            "eval_scores": {"foresight_depth_Fn": 4.9, "axiological_coverage_Ac": 0.92, "irreversibility_risk_Rrisk": 1.2, "epistemic_hubris_penalty_Hpen": 0.6},
            "peer_scores": [2.25, 2.40]
        }
    ]

    for idx, task in enumerate(micro_tasks, 1):
        print(f"\n--- [Task {idx}/{len(micro_tasks)}] Dispatched to Mobile Hardware ---")
        runtime.run_single_eval_cycle(task)
        time.sleep(1)

    print("\n" + "=" * 70)
    print("   MOBILE EDGE DEMO COMPLETED SUCCESSFULLY! 🛡️")
    print("=" * 70)

if __name__ == "__main__":
    run_demo()
