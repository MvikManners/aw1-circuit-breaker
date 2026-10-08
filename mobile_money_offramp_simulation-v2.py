"""
===================================================================================
LAVETO WISDOM (AW-1) — MOBILE MONEY OFF-RAMP SIMULATION (V2)
===================================================================================
"""
import sys, os, time, json, hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List

for search_dir in ["/home/LavetoLab", "/home/LavetoLab/laveto_wisdom", "."]:
    if os.path.exists(search_dir) and search_dir not in sys.path:
        sys.path.insert(0, search_dir)

from tokenomics_engine import TokenomicsConstants, PoUCOffRampCalculator, SovereignTreasuryState

class MobileMoneyOffRampSimulator:
    SUPPORTED_CARRIERS = {
        "ORANGE_MONEY": {"name": "Orange Money Botswana", "prefix": "+267 72"},
        "MASCOM_MYZAKA": {"name": "Mascom MyZaka", "prefix": "+267 71"},
        "BTC_SMEGA": {"name": "BTC Smega", "prefix": "+267 73"},
        "LAVETO_PAY_MERCHANT": {"name": "Laveto Pay (In-Store Merchant)", "prefix": "POS-STORE"}
    }
    def __init__(self, treasury: SovereignTreasuryState):
        self.treasury = treasury

    def simulate_user_cashout(self, scenario_title: str, node_id: str, awt_amount: float, carrier_key: str, phone_number: str, is_internal_spend: bool = False) -> Dict[str, Any]:
        carrier = self.SUPPORTED_CARRIERS.get(carrier_key, self.SUPPORTED_CARRIERS["ORANGE_MONEY"])
        print("\n" + "=" * 80)
        print(f" 📲 SIMULATING CASHOUT SCENARIO: {scenario_title.upper()}")
        print("=" * 80)
        print(f"  • Node Operator      : {node_id}")
        print(f"  • AWT to Cash Out    : {awt_amount:,.2f} AWT (@ P{TokenomicsConstants.BASE_SPOT_RATE_BWP:.2f}/AWT)")
        print(f"  • Destination Rail   : {carrier['name']} ({phone_number})")
        print(f"  • Spend Mode         : {'🛒 In-Ecosystem Merchant Spend' if is_internal_spend else '🏦 External Mobile Money Cash-Out'}")
        print("-" * 80)
        result = self.treasury.process_offramp_transaction(node_id=node_id, awt_amount=awt_amount, destination_msisdn=phone_number, is_internal_spend=is_internal_spend)
        quote = result["calculation"]
        waterfall = quote["waterfall_allocations"]
        print(f"  📊 FINANCIAL SETTLEMENT BREAKDOWN:")
        print(f"    - Gross Economic Value   : P{quote['gross_bwp_value']:,.2f}")
        print(f"    - Fee Tier Triggered     : {quote['tier_applied']} ({quote['exit_fee_rate_pct']}%)")
        print(f"    - Gross Protocol Exit Fee: P{quote['gross_fee_bwp']:,.2f}")
        print(f"    - Carrier API Cost (1.2%): P{quote['carrier_clearing_cost_bwp']:,.2f}")
        print(f"    -------------------------------------------------------")
        print(f"    💰 NET CITIZEN CASH DISBURSED: P{quote['net_citizen_payout_bwp']:,.2f} ({quote['citizen_payout_pct']}% of Gross)")
        print(f"    -------------------------------------------------------")
        if not is_internal_spend:
            print(f"  🏛️ THREE-WAY PROTOCOL SURPLUS WATERFALL (Net Surplus: P{quote['protocol_net_surplus_bwp']:,.2f}):")
            print(f"    1. BoB 1-to-1 Reserve Vault (50%) : +P{waterfall['treasury_reserve_vault_bwp']:,.2f} (Fiat liquidity shield)")
            print(f"    2. Buyback & Burn Vault (30%)     : +P{waterfall['buyback_and_burn_vault_bwp']:,.2f} (~{waterfall['awt_burned_estimate']} AWT burned)")
            print(f"    3. Laveto Operating Pool (20%)    : +P{waterfall['operating_partner_pool_bwp']:,.2f} (Commercial revenue share)")
        else:
            print(f"  ✨ GRAVITY WELL EFFECT: 0% FEE APPLIED!")
            print(f"    Citizen preserves 100% of purchasing power (P{quote['net_citizen_payout_bwp']:,.2f}) by spending in-store.")
        print(f"\n  🔒 CRYPTOGRAPHIC ASSURANCE AUDIT:")
        print(f"    - Status          : {result['status']}")
        print(f"    - Dossier Hash    : {result['dossier_hash']}")
        print(f"    - Post-Vault Cash : P{result['treasury_state_post_tx']['fiat_reserve_vault_bwp']:,.2f}")
        return result

def run_full_simulation_suite():
    print("=" * 80)
    print(" 🚀 LAVETO WISDOM (AW-1) — 10% TO 15% POUC OFF-RAMP VERIFICATION ENGINE")
    print("=" * 80)
    treasury = SovereignTreasuryState(initial_fiat_reserve_bwp=500_000.0)
    sim = MobileMoneyOffRampSimulator(treasury)

    # 1. Micro (< P250) -> 15.0%
    q1 = sim.simulate_user_cashout("Micro Cash-Out (< P250)", "node-gaborone-041", 80.0, "ORANGE_MONEY", "+267 72 104 891")["calculation"]
    assert q1["exit_fee_rate_pct"] == 15.0 and q1["net_citizen_payout_bwp"] == 170.0 and q1["protocol_net_surplus_bwp"] == 27.60

    # 2. Standard (P250 - P1,000) -> 12.5%
    q2 = sim.simulate_user_cashout("Standard Cash-Out (P250 - P1,000)", "node-francistown-112", 200.0, "MASCOM_MYZAKA", "+267 71 883 204")["calculation"]
    assert q2["exit_fee_rate_pct"] == 12.5 and q2["net_citizen_payout_bwp"] == 437.50 and q2["protocol_net_surplus_bwp"] == 56.50

    # 3. Bulk (> P1,000) -> 10.0%
    q3 = sim.simulate_user_cashout("Bulk Guild Master Cash-Out (> P1,000)", "node-palapye-biust-guild", 600.0, "BTC_SMEGA", "+267 73 992 018")["calculation"]
    assert q3["exit_fee_rate_pct"] == 10.0 and q3["net_citizen_payout_bwp"] == 1350.00 and q3["protocol_net_surplus_bwp"] == 132.00

    # 4. In-Store Spend -> 0.0%
    q4 = sim.simulate_user_cashout("In-Store Grocery Spend", "node-gaborone-041", 200.0, "LAVETO_PAY_MERCHANT", "POS-CHOPIES-TLOKWENG", is_internal_spend=True)["calculation"]
    assert q4["exit_fee_rate_pct"] == 0.0 and q4["net_citizen_payout_bwp"] == 500.00

    print("\n" + "=" * 80)
    print(" 🟢 ALL 4 OFF-RAMP SCENARIOS 100% VERIFIED & MATHEMATICALLY PROVEN")
    print("=" * 80)

if __name__ == "__main__":
    run_full_simulation_suite()
