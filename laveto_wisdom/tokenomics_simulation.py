"""
===============================================================================
LAVETO WISDOM (AW-1) — TOKENOMICS & CITIZEN EARNINGS SIMULATION ENGINE
===============================================================================
Module: tokenomics_simulation.py
Purpose: Simulates enterprise BWP audit volume scenarios, 20% buyback-and-burn
         impact, liquidity pool depth, and projected daily/monthly AWT & BWP
         earnings for individual Batswana smartphone and PC node operators.
===============================================================================
"""

import json
from .tokenomics_engine import TokenomicsEngine
import os

def run_simulation():
    AVG_AUDIT_FEE_BWP = 50000.0  # Average BWP 50,000 per enterprise decision audit
    BUYBACK_BURN_PCT = 0.20        # 20% automatically bought back & burned
    CITIZEN_REWARD_POOL_PCT = 0.45 # 45% routed to active node rewards
    TREASURY_OPS_PCT = 0.35        # 35% retained for reserve & infrastructure
    
    AWT_SPOT_PRICE_BWP = 2.50    # Initial spot rate: 1 AWT = BWP 2.50
    TOTAL_AWT_SUPPLY = 1000000000 # 1 Billion hard cap
    
    scenarios = [
        ("Phase 1: Initial CEDA/SEZA Pilots", 10, 1000),
        ("Phase 2: National Growth (Banking & Tenders)", 50, 5000),
        ("Phase 3: Full National Scale (Botswana Economy)", 200, 25000),
        ("Phase 4: Pan-African Expansion", 1000, 100000),
    ]

    print("=" * 80)
    print("   📊 LAVETO WISDOM (AW-1) TOKENOMICS & CITIZEN EARNINGS SIMULATOR")
    print("=" * 80)
    print(f"  • Base Audit Fee         : BWP {AVG_AUDIT_FEE_BWP:,.2f}")
    print(f"  • Buyback & Burn Rate    : {BUYBACK_BURN_PCT*100:.0f}%")
    print(f"  • Initial Spot Exchange  : 1 AWT = BWP {AWT_SPOT_PRICE_BWP:.2f}")
    print("=" * 80)

    for name, monthly_audits, active_nodes in scenarios:
        gross_monthly_bwp = monthly_audits * AVG_AUDIT_FEE_BWP
        monthly_burn_bwp = gross_monthly_bwp * BUYBACK_BURN_PCT
        monthly_reward_pool_bwp = gross_monthly_bwp * CITIZEN_REWARD_POOL_PCT
        monthly_treasury_bwp = gross_monthly_bwp * TREASURY_OPS_PCT
        
        monthly_awt_burned = monthly_burn_bwp / AWT_SPOT_PRICE_BWP
        annual_awt_burned = monthly_awt_burned * 12
        pct_supply_burned_annual = (annual_awt_burned / TOTAL_AWT_SUPPLY) * 100

        payout_per_node_bwp_month = monthly_reward_pool_bwp / active_nodes
        payout_per_node_awt_month = payout_per_node_bwp_month / AWT_SPOT_PRICE_BWP
        payout_per_node_bwp_daily = payout_per_node_bwp_month / 30.0
        payout_per_node_awt_daily = payout_per_node_awt_month / 30.0

        print(f"\n📌 {name.upper()}")
        print("-" * 80)
        print(f"  • Enterprise Volume     : {monthly_audits} audits/month | BWP {gross_monthly_bwp:,.2f} Gross Revenue")
        print(f"  • 20% Buyback & Burn    : BWP {monthly_burn_bwp:,.2f}/mo (🔥 {monthly_awt_burned:,.0f} AWT/mo burned)")
        print(f"  • Annual Supply Burned  : {annual_awt_burned:,.0f} AWT/year ({pct_supply_burned_annual:.2f}% of supply)")
        print(f"  • Citizen Reward Pool   : BWP {monthly_reward_pool_bwp:,.2f}/mo distributed to {active_nodes:,} nodes")
        print(f"  ----------------------------------------------------------------------------")
        print(f"  💰 AVERAGE CITIZEN EARNINGS PER NODE:")
        print(f"     - Monthly : {payout_per_node_awt_month:,.1f} AWT  (≈ BWP {payout_per_node_bwp_month:,.2f})")
        print(f"     - Daily   : {payout_per_node_awt_daily:,.1f} AWT  (≈ BWP {payout_per_node_bwp_daily:,.2f})")
        print("=" * 80)

if __name__ == "__main__":
    run_simulation()