import json
import sys

sys.path.insert(0, '/home/LavetoLab')
sys.path.insert(0, '/home/LavetoLab/laveto_wisdom')

from flask import Flask
from routes_reward_integration import aw_reward_bp
from tokenomics_engine import TokenomicsEngine

def run_end_to_end_verification():
    app = Flask(__name__)
    app.register_blueprint(aw_reward_bp)
    client = app.test_client()

    print("=" * 80)
    print("  🧪 LAVETO WISDOM (AW-1) END-TO-END SETTLEMENT & BURN VERIFICATION")
    print("=" * 80)

    # 1. Initialize Wallets (Ambassador + Recruited Node)
    engine = TokenomicsEngine()
    ambassador_id = "node-bw-ambassador-707"
    recruited_id = "node-bw-gaborone-991"
    
    engine.get_or_create_wallet(ambassador_id)
    engine.get_or_create_wallet(recruited_id, referred_by=ambassador_id)

    print(f"\n[1] Initialized Wallets:")
    print(f"  • Ambassador Node : {ambassador_id}")
    print(f"  • Recruited Node  : {recruited_id} (Referred by {ambassador_id})")

    # 2. Test Enterprise Audit Endpoint (20% Buyback & Burn)
    print(f"\n[2] Executing Enterprise Audit via POST /v1/aw/audit...")
    audit_payload = {
        "dilemma_id": "AUDIT-SEZA-2026-SOLAR-PH3",
        "audit_fee_bwp": 50000.0,
        "awt_market_price_bwp": 2.50
    }
    audit_res = client.post('/v1/aw/audit', data=json.dumps(audit_payload), content_type='application/json')
    audit_data = audit_res.get_json()
    print(f"  ✓ HTTP Status Code : {audit_res.status_code}")
    print(f"  ✓ Audit Status     : {audit_data['audit_result']['status']}")
    print(f"  ✓ Burn Receipt Hash: {audit_data['buyback_and_burn_receipt']['tx_hash']}")
    print(f"  🔥 BWP Burned (20%): BWP {audit_data['buyback_and_burn_receipt']['bwp_burned']:,.2f}")
    print(f"  🔥 AWT Burned      : {audit_data['buyback_and_burn_receipt']['awt_burned']:,.2f} AWT")

    # 3. Test PoUC Edge Node Submission & 5% Referral Override
    print(f"\n[3] Submitting PoUC Task via POST /v1/aw/pouc/submit...")
    pouc_payload = {
        "node_id": recruited_id,
        "task_id": "task-chobe-grain-transit-audit",
        "telemetry": {
            "device_type": "DESKTOP",
            "power_source": "AC_CHARGING",
            "network_type": "UNMETERED_WIFI",
            "battery_level_percent": 95.0,
            "thermal_state_celsius": 42.0
        },
        "scores": {"foresight_depth": 3.0, "axiological_coverage": 1.0, "irreversibility_risk": 1.0, "epistemic_hubris_penalty": 0.2},
        "surfaced_blindspot": "Subcontracting tender for North-East District transmission line lacks 50% statutory CEE local labor guarantees.",
        "peer_scores": [2.45, 2.50, 2.55]
    }
    pouc_res = client.post('/v1/aw/pouc/submit', data=json.dumps(pouc_payload), content_type='application/json')
    pouc_data = pouc_res.get_json()

    receipt = pouc_data['settlement_receipt']
    print(f"  ✓ HTTP Status Code : {pouc_res.status_code}")
    print(f"  ✓ Network Status   : {pouc_data['status']}")
    print(f"  ✓ Wisdom Quotient W: {pouc_data['wisdom_quotient_W']}")
    print(f"  ✓ Epistemic Delta  : {pouc_data['epistemic_delta']}x")
    print(f"  💰 Node Earned     : +{receipt['final_awt_earned']} AWT | +{receipt['w_tau_credited']:.3f} W_tau")
    print(f"  🎁 5% Referral Paid: +{receipt['referral_royalty_dispatched']} AWT -> Dispatched to {ambassador_id}")

    # 4. Query Tokenomics Summary
    print(f"\n[4] Querying Tokenomics Ledger via GET /v1/aw/tokenomics/summary...")
    summary_res = client.get('/v1/aw/tokenomics/summary')
    summary_data = summary_res.get_json()
    
    print(f"  ✓ HTTP Status Code   : {summary_res.status_code}")
    print(f"  🌐 Circulating Supply: {summary_data['circulating_supply']:,.2f} AWT")
    print(f"  🔥 Total Burned AWT  : {summary_data['total_burned']:,.2f} AWT")
    print(f"  🏦 Treasury Reserve  : BWP {summary_data['treasury_bwp_reserve']:,.2f}")

    print("\n" + "=" * 80)
    print("  END-TO-END SETTLEMENT & BURN VERIFICATION COMPLETE 🛡️")
    print("=" * 80)

if __name__ == '__main__':
    run_end_to_end_verification()
