"""
===================================================================================
                   LAVETO WISDOM (AW-1) SOVEREIGN TOKENOMICS ENGINE
===================================================================================
File: tokenomics_engine.py
Version: 2.0 (Institutional Off-Ramp Toll Specification)
Author: Manners Vela Ikhutseng — Founder & Sovereign Architect
Description: Core economic execution engine governing:
             1. Fixed 1 Billion AWT supply cap & Soulbound Reputation (W_tau) firewall.
             2. Proof of Useful Contribution (PoUC) emissions tied to institutional BWP inflows.
             3. Tiered 10% to 15% PoUC mobile money off-ramp exit toll & 0% internal spend.
             4. 3-Way Waterfall Allocation: 50% Reserve Vault, 30% Buyback & Burn, 20% Ops.
             5. Backward compatible with routes_reward_integration.py and test_all.sh.
===================================================================================
"""

import time
import math
import hashlib
import os
import sqlite3
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional


class TokenomicsConstants:
    TOTAL_AWT_SUPPLY_CAP = 1_000_000_000.0  # 1 Billion Fixed Cap
    BASE_SPOT_RATE_BWP = 2.50               # 1 AWT = BWP 2.50
    CARRIER_TELCO_FEE_RATE = 0.012          # 1.2% Direct Carrier Clearing Cost (Orange/Mascom)

    # Off-Ramp Exit Toll Schedule
    TIER_3_MICRO_THRESHOLD = 250.0          # Below P250.00 BWP
    TIER_2_STANDARD_THRESHOLD = 1000.0      # P250.00 to P1,000.00 BWP

    RATE_TIER_3_MICRO = 0.150               # 15.0% Exit Toll
    RATE_TIER_2_STANDARD = 0.125            # 12.5% Exit Toll
    RATE_TIER_1_BULK = 0.100                # 10.0% Exit Toll (> P1,000.00)
    RATE_INTERNAL_SPEND = 0.000             # 0.0% (Zero Fee for Laveto Pay Merchants)

    # Surplus Waterfall Allocations
    WATERFALL_RESERVE_SHARE = 0.50          # 50% to BoB 1-to-1 Liquidity Reserve
    WATERFALL_BURN_SHARE = 0.30             # 30% to Automated Open-Market Buyback & Burn
    WATERFALL_OPERATING_SHARE = 0.20        # 20% to Laveto Operations & Partner Pool


class PoUCOffRampCalculator:
    """
    Calculates exit tolls, telco carrier pass-throughs, net citizen payouts,
    and protocol waterfall allocations for PoUC token redemptions.
    """

    @classmethod
    def determine_exit_fee_rate(cls, gross_bwp: float, is_internal_spend: bool = False) -> Tuple[float, str]:
        if is_internal_spend:
            return TokenomicsConstants.RATE_INTERNAL_SPEND, "INTERNAL_MERCHANT_SPEND_0_PCT"

        if gross_bwp < TokenomicsConstants.TIER_3_MICRO_THRESHOLD:
            return TokenomicsConstants.RATE_TIER_3_MICRO, "TIER_3_MICRO_15_PCT"
        elif gross_bwp <= TokenomicsConstants.TIER_2_STANDARD_THRESHOLD:
            return TokenomicsConstants.RATE_TIER_2_STANDARD, "TIER_2_STANDARD_12_5_PCT"
        else:
            return TokenomicsConstants.RATE_TIER_1_BULK, "TIER_1_BULK_GUILD_10_PCT"

    @classmethod
    def calculate_redemption(
        cls,
        awt_amount: float,
        spot_rate_bwp: float = TokenomicsConstants.BASE_SPOT_RATE_BWP,
        is_internal_spend: bool = False
    ) -> Dict[str, Any]:
        """
        Executes complete mathematical breakdown of an AWT redemption request.
        """
        gross_bwp = round(awt_amount * spot_rate_bwp, 2)
        fee_rate, tier_name = cls.determine_exit_fee_rate(gross_bwp, is_internal_spend)

        # 1. Total Protocol Fee
        gross_fee_bwp = round(gross_bwp * fee_rate, 2)
        net_citizen_bwp = round(gross_bwp - gross_fee_bwp, 2)

        # 2. Carrier Cost vs Protocol Surplus
        if is_internal_spend or gross_fee_bwp == 0.0:
            carrier_cost_bwp = 0.0
            protocol_surplus_bwp = 0.0
            reserve_allocation_bwp = 0.0
            burn_allocation_bwp = 0.0
            operating_allocation_bwp = 0.0
            awt_burned = 0.0
        else:
            carrier_cost_bwp = round(gross_bwp * TokenomicsConstants.CARRIER_TELCO_FEE_RATE, 2)
            protocol_surplus_bwp = max(0.0, round(gross_fee_bwp - carrier_cost_bwp, 2))

            # 3. 3-Way Waterfall Split
            reserve_allocation_bwp = round(protocol_surplus_bwp * TokenomicsConstants.WATERFALL_RESERVE_SHARE, 2)
            burn_allocation_bwp = round(protocol_surplus_bwp * TokenomicsConstants.WATERFALL_BURN_SHARE, 2)
            operating_allocation_bwp = round(protocol_surplus_bwp * TokenomicsConstants.WATERFALL_OPERATING_SHARE, 2)

            # Reconciliation adjustment for cent rounding
            allocated_sum = reserve_allocation_bwp + burn_allocation_bwp + operating_allocation_bwp
            diff = round(protocol_surplus_bwp - allocated_sum, 2)
            if diff != 0:
                reserve_allocation_bwp = round(reserve_allocation_bwp + diff, 2)

            awt_burned = round(burn_allocation_bwp / max(0.01, spot_rate_bwp), 2)

        return {
            "awt_amount_redeemed": awt_amount,
            "spot_rate_bwp": spot_rate_bwp,
            "gross_bwp_value": gross_bwp,
            "is_internal_spend": is_internal_spend,
            "tier_applied": tier_name,
            "exit_fee_rate_pct": round(fee_rate * 100, 2),
            "gross_fee_bwp": gross_fee_bwp,
            "net_citizen_payout_bwp": net_citizen_bwp,
            "citizen_payout_pct": round((net_citizen_bwp / max(0.01, gross_bwp)) * 100, 2),
            "carrier_clearing_cost_bwp": carrier_cost_bwp,
            "protocol_net_surplus_bwp": protocol_surplus_bwp,
            "waterfall_allocations": {
                "treasury_reserve_vault_bwp": reserve_allocation_bwp,
                "buyback_and_burn_vault_bwp": burn_allocation_bwp,
                "operating_partner_pool_bwp": operating_allocation_bwp,
                "awt_burned_estimate": awt_burned
            }
        }


class SovereignTreasuryState:
    """
    Stateful ledger maintaining live balances of the Bank of Botswana 1-to-1 cash vault,
    circulating supply, and cumulative burn counters.
    """

    def __init__(self, initial_fiat_reserve_bwp: float = 500_000.0):
        self.fiat_reserve_vault_bwp = initial_fiat_reserve_bwp
        self.circulating_awt_supply = 10_000_000.0
        self.cumulative_awt_burned = 0.0
        self.cumulative_fiat_distributed_bwp = 0.0
        self.total_transactions_settled = 0

    def get_reserve_backing_ratio(self, spot_rate_bwp: float = TokenomicsConstants.BASE_SPOT_RATE_BWP) -> float:
        circulating_value_bwp = self.circulating_awt_supply * spot_rate_bwp
        if circulating_value_bwp <= 0:
            return 1.0
        return round(self.fiat_reserve_vault_bwp / circulating_value_bwp, 4)

    def process_offramp_transaction(
        self,
        node_id: str,
        awt_amount: float,
        spot_rate_bwp: float = TokenomicsConstants.BASE_SPOT_RATE_BWP,
        destination_msisdn: str = "+26771234567",
        is_internal_spend: bool = False
    ) -> Dict[str, Any]:
        calc = PoUCOffRampCalculator.calculate_redemption(awt_amount, spot_rate_bwp, is_internal_spend)
        now_str = datetime.now(timezone.utc).isoformat()

        net_payout = calc["net_citizen_payout_bwp"]
        waterfall = calc["waterfall_allocations"]

        self.fiat_reserve_vault_bwp += waterfall["treasury_reserve_vault_bwp"]
        self.fiat_reserve_vault_bwp -= net_payout
        self.cumulative_fiat_distributed_bwp += net_payout

        self.circulating_awt_supply -= awt_amount
        self.cumulative_awt_burned += waterfall["awt_burned_estimate"]
        self.total_transactions_settled += 1

        tx_payload = f"{node_id}:{awt_amount}:{net_payout}:{destination_msisdn}:{now_str}"
        dossier_hash = "0x" + hashlib.sha256(tx_payload.encode()).hexdigest()

        return {
            "status": "SETTLED_SUCCESSFULLY",
            "node_id": node_id,
            "destination_msisdn": destination_msisdn,
            "timestamp": now_str,
            "calculation": calc,
            "dossier_hash": dossier_hash,
            "treasury_state_post_tx": {
                "fiat_reserve_vault_bwp": round(self.fiat_reserve_vault_bwp, 2),
                "circulating_awt_supply": round(self.circulating_awt_supply, 2),
                "cumulative_awt_burned": round(self.cumulative_awt_burned, 2),
                "total_settled_count": self.total_transactions_settled
            }
        }


class TokenomicsEngine:
    """
    Unified Production Tokenomics Engine maintaining full backward compatibility
    with routes_reward_integration.py and test_all.sh.
    """

    def __init__(self, db_path: str = "/home/LavetoLab/lvt_backend/lvt_database.db"):
        self.MAX_AWT_SUPPLY = TokenomicsConstants.TOTAL_AWT_SUPPLY_CAP
        self.DEFAULT_AWT_BWP_SPOT_RATE = TokenomicsConstants.BASE_SPOT_RATE_BWP
        self.db_path = db_path
        self.treasury = SovereignTreasuryState()

    def settle_node_payout(
        self,
        node_address: str,
        task_id: str,
        base_awt: float = 10.0,
        epistemic_delta: float = 1.0
    ) -> Dict[str, Any]:
        awt = round(base_awt * epistemic_delta, 2)
        return {
            "node_address": node_address,
            "task_id": task_id,
            "awt_minted": awt,
            "w_tau_credited": 0.05,
            "referral_royalty_awt": round(awt * 0.05, 2)
        }

    def process_enterprise_buyback_and_burn(self, *args, **kwargs) -> Dict[str, Any]:
        if "gross_bwp_fee" in kwargs:
            fee = float(kwargs.get("gross_bwp_fee", 0.0))
            ref_id = str(kwargs.get("reference_id", "REF-DEFAULT"))
            enterprise_id = str(kwargs.get("enterprise_id", "ENTERPRISE-DEFAULT"))
            spot = float(kwargs.get("spot_rate", self.DEFAULT_AWT_BWP_SPOT_RATE))
            service_type = kwargs.get("service_type", "SEZA_ENTERPRISE_AUDIT")

            if os.path.exists(self.db_path):
                try:
                    conn = sqlite3.connect(self.db_path, timeout=5.0)
                    cur = conn.cursor()
                    cur.execute("SELECT id FROM enterprise_burn_ledger WHERE reference_id = ?;", (ref_id,))
                    if cur.fetchone():
                        conn.close()
                        return {"status": "REJECTED_DUPLICATE_REFERENCE", "error": f"Enterprise reference '{ref_id}' already processed."}
                    conn.close()
                except Exception:
                    pass

            burn_budget = round(fee * 0.20, 2)
            burned_awt = round(burn_budget / max(0.01, spot), 2)
            burn_hash = "0x" + hashlib.sha256(f"{ref_id}:{burned_awt}".encode()).hexdigest()
            return {
                "status": "SUCCESS", "enterprise_id": enterprise_id, "reference_id": ref_id,
                "service_type": service_type, "gross_bwp_fee": fee, "burn_budget_bwp": burn_budget,
                "awt_burned": burned_awt, "burn_tx_hash": burn_hash
            }

        audit_id = str(args[0]) if len(args) > 0 else kwargs.get("audit_id", "AUDIT-DEFAULT")
        fee = float(args[1]) if len(args) > 1 else float(kwargs.get("fee", kwargs.get("audit_fee_bwp", 25000.0)))
        spot = float(args[2]) if len(args) > 2 else float(kwargs.get("spot", kwargs.get("awt_market_price_bwp", 2.50)))
        burn_budget = round(fee * 0.20, 2)
        burned_awt = round(burn_budget / max(0.01, spot), 2)
        burn_hash = "0x" + hashlib.sha256(f"{audit_id}:{burned_awt}".encode()).hexdigest()
        return {
            "status": "SUCCESS", "audit_id": audit_id, "fee_bwp": fee,
            "burn_budget_bwp": burn_budget, "awt_burned": burned_awt, "burn_tx_hash": burn_hash
        }

    def get_tokenomics_summary(self) -> Dict[str, Any]:
        return {
            "status": "SUCCESS",
            "max_supply_awt": self.MAX_AWT_SUPPLY,
            "circulating_supply_awt": round(self.treasury.circulating_awt_supply, 2),
            "total_burned_awt": round(self.treasury.cumulative_awt_burned, 2),
            "treasury_bwp_reserve": round(self.treasury.fiat_reserve_vault_bwp, 2),
            "spot_rate_bwp": self.DEFAULT_AWT_BWP_SPOT_RATE,
            "reserve_backing_ratio": self.treasury.get_reserve_backing_ratio()
        }
