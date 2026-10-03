"""
===================================================================================
LAVETO WISDOM (AW-1) — MOBILE MONEY & BANKING OFF-RAMP SIMULATOR (LAVETO_PAY INTEGRATED)
===================================================================================
File: mobile_money_offramp_simulation-v2.py
Description: Simulates real-time fiat cash-outs for Batswana node operators by
             integrating directly with `laveto_pay.py` payment gateway engine.
===================================================================================
"""

import sys
import os
import json

# Ensure parent directories are on path for direct script execution
sys.path.insert(0, '/home/LavetoLab')
sys.path.insert(0, '/home/LavetoLab/laveto_wisdom')

try:
    from laveto_pay import LavetoPayEngine
except ImportError:
    from .laveto_pay import LavetoPayEngine

def get_offramp_simulation_data():
    """
    Returns structured simulation data for live web dashboard and REST API consumption.
    """
    pay_engine = LavetoPayEngine(treasury_reserve_bwp=540000.0)

    tier_scenarios = [
        {
            "tier": "Micro Node (Smartphone)",
            "node_id": "node-bw-gaborone-881",
            "awt_mined_monthly": 90.0,
            "account": "+26771882901"
        },
        {
            "tier": "Power Node (Desktop PC)",
            "node_id": "node-bw-francistown-204",
            "awt_mined_monthly": 250.0,
            "account": "+26772991042"
        },
        {
            "tier": "Community Ambassador (5% Referrals)",
            "node_id": "node-bw-ambassador-707",
            "awt_mined_monthly": 750.0,
            "account": "+26773551109"
        }
    ]

    providers_to_test = ["ORANGE_MONEY", "MASCOM_MYZAKA", "BANK_EFT", "CARDLESS_ATM"]
    disbursements = []

    for tier in tier_scenarios:
        for p_key in providers_to_test:
            receipt = pay_engine.process_offramp_disbursement(
                node_address=tier["node_id"],
                awt_amount=tier["awt_mined_monthly"],
                provider_key=p_key,
                phone_or_account=tier["account"]
            )
            receipt["tier"] = tier["tier"]
            disbursements.append(receipt)

    return {
        "status": "SUCCESS",
        "initial_treasury_bwp": 540000.00,
        "remaining_treasury_bwp": pay_engine.treasury_reserve_bwp,
        "spot_rate_bwp": pay_engine.spot_rate_bwp,
        "supported_providers": LavetoPayEngine.SUPPORTED_PROVIDERS,
        "disbursements": disbursements
    }

def simulate_mobile_money_offramp():
    """
    CLI execution runner demonstrating multi-tier payouts and partner gateway settlement.
    """
    pay_engine = LavetoPayEngine(treasury_reserve_bwp=540000.0)

    tier_scenarios = [
        {
            "tier": "Micro Node (Smartphone)",
            "node_id": "node-bw-gaborone-881",
            "awt_mined_monthly": 90.0,
            "account": "+26771882901"
        },
        {
            "tier": "Power Node (Desktop PC)",
            "node_id": "node-bw-francistown-204",
            "awt_mined_monthly": 250.0,
            "account": "+26772991042"
        },
        {
            "tier": "Community Ambassador (5% Referrals)",
            "node_id": "node-bw-ambassador-707",
            "awt_mined_monthly": 750.0,
            "account": "+26773551109"
        }
    ]

    providers_to_test = ["ORANGE_MONEY", "MASCOM_MYZAKA", "BANK_EFT", "CARDLESS_ATM"]

    print("================================================================================")
    print("   📱 LAVETO WISDOM (AW-1) MOBILE MONEY & BANKING OFF-RAMP SIMULATOR")
    print("================================================================================")
    print("  • Payment Engine     : laveto_pay.py (Integrated Gateway)")
    print("  • Target Market      : Botswana (BWP Pula Settlement)")
    print("  • Initial Treasury   : BWP 540,000.00 Enterprise Audit Fee Liquidity Reserve")
    print("================================================================================\n")

    print("📌 PARTNER GATEWAY FEE & SETTLEMENT ARCHITECTURE")
    print("-" * 80)
    for p_key, p in LavetoPayEngine.SUPPORTED_PROVIDERS.items():
        print(f"  • {p['name']} ({p['type']}) [{p_key}]")
        print(f"    - Fee: {p['fee_pct']}% | Settlement: {p['settlement_speed']} | Daily Limit: BWP {p['daily_limit_bwp']:,}")
    print("\n" + "=" * 80 + "\n")

    print("📌 EXECUTING REAL-TIME OFF-RAMP DISPATCHES VIA LAVETO_PAY.PY")
    print("-" * 80)

    for tier in tier_scenarios:
        print(f"👤 {tier['tier']} [{tier['node_id']}]")
        print(f"   • Monthly Mined : {tier['awt_mined_monthly']} AWT (≈ BWP {tier['awt_mined_monthly'] * 2.50:.2f})")
        print("   • Disbursing Across Channels:")

        for p_key in providers_to_test:
            receipt = pay_engine.process_offramp_disbursement(
                node_address=tier["node_id"],
                awt_amount=tier["awt_mined_monthly"],
                provider_key=p_key,
                phone_or_account=tier["account"]
            )

            voucher_info = f" | PIN: {receipt['voucher_pin']}" if receipt.get('voucher_pin') else ""
            print(f"     → [{receipt['provider']}]")
            print(f"       - Net Cash Payout : BWP {receipt['net_bwp_disbursed']:.2f} (Fee: BWP {receipt['gateway_fee_bwp']:.2f} @ {receipt['gateway_fee_pct']}%)")
            print(f"       - Transaction Ref : {receipt['disbursement_id']}{voucher_info}")
            print(f"       - Delivery Speed  : {receipt['settlement_speed']}")
        print("  " + "-" * 70)

    print("\n================================================================================")
    print(f"🏦 REMAINING TREASURY LIQUIDITY RESERVE: BWP {pay_engine.treasury_reserve_bwp:,.2f}")
    print("================================================================================")

if __name__ == "__main__":
    simulate_mobile_money_offramp()