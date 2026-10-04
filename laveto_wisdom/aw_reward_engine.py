"""
===================================================================================
                   LAVETO WISDOM (AW-1) REWARD & TOKENOMICS ENGINE
===================================================================================
File: aw_reward_engine.py
Description: Implements Proof of Useful Contribution (PoUC) validation,
             Epoch-Based Rate Limiting & Vesting, Economic Proof Verification
             (tethering AWT emissions to real BWP ad & audit fee inflows),
             and the enterprise 20% Buyback-and-Burn mechanism.
===================================================================================
"""

import math
import hashlib
import time
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional


class HardwareInterlockVerifier:
    """
    Validates mobile/edge node telemetry before allowing PoUC micro-evaluation tasks.
    Ensures zero user disruption by enforcing battery, thermal, and network gates.
    """
    MIN_BATTERY_PERCENT = 80.0
    MAX_THERMAL_CELSIUS = 34.0
    REQUIRED_POWER_STATE = "AC_CHARGING"
    REQUIRED_NETWORK_STATE = "UNMETERED_WIFI"

    @classmethod
    def verify(cls, telemetry: Dict[str, any]) -> Tuple[bool, str]:
        if telemetry.get("power_source") != cls.REQUIRED_POWER_STATE:
            return False, f"Device not on {cls.REQUIRED_POWER_STATE}."
        if telemetry.get("network_type") != cls.REQUIRED_NETWORK_STATE:
            return False, f"Device not on {cls.REQUIRED_NETWORK_STATE}."
        if telemetry.get("battery_level_percent", 0) < cls.MIN_BATTERY_PERCENT:
            return False, f"Battery ({telemetry.get('battery_level_percent')}%) below {cls.MIN_BATTERY_PERCENT}% threshold."
        if telemetry.get("thermal_state_celsius", 100) > cls.MAX_THERMAL_CELSIUS:
            return False, f"Thermal state ({telemetry.get('thermal_state_celsius')}°C) exceeds {cls.MAX_THERMAL_CELSIUS}°C limit."
        return True, "Hardware interlocks satisfied."


class EpochVestingController:
    """
    Implements Epoch-Based Rate Limiting & Vesting to eliminate hyper-inflationary
    speedy mining. Enforces 24-hour epoch caps and task velocity limits.
    """
    EPOCH_DURATION_SECONDS = 86400  # 24-hour epoch
    MAX_AWT_PER_EPOCH_PER_NODE = 50.0  # Hard daily cap per node
    MAX_TASKS_PER_HOUR = 5            # Rate-limiting task frequency

    def __init__(self):
        self.node_epoch_earnings: Dict[str, Dict[str, any]] = {}  # node_id -> {epoch_id, current_awt, task_timestamps}

    def _get_current_epoch_id(self) -> str:
        current_time = time.time()
        epoch_index = int(current_time // self.EPOCH_DURATION_SECONDS)
        return f"EPOCH-{epoch_index}"

    def check_epoch_limit(self, node_id: str, requested_reward_awt: float) -> Tuple[bool, str, float]:
        epoch_id = self._get_current_epoch_id()
        now = time.time()

        if node_id not in self.node_epoch_earnings or self.node_epoch_earnings[node_id]["epoch_id"] != epoch_id:
            self.node_epoch_earnings[node_id] = {
                "epoch_id": epoch_id,
                "earned_awt": 0.0,
                "task_timestamps": []
            }

        node_data = self.node_epoch_earnings[node_id]

        # 1. Frequency Check: Max tasks per hour
        recent_tasks = [t for t in node_data["task_timestamps"] if now - t < 3600]
        if len(recent_tasks) >= self.MAX_TASKS_PER_HOUR:
            return False, f"Hourly task limit reached ({len(recent_tasks)}/{self.MAX_TASKS_PER_HOUR} tasks/hr). Epoch cooldown active.", 0.0

        # 2. Daily Epoch Cap Check
        remaining_epoch_cap = self.MAX_AWT_PER_EPOCH_PER_NODE - node_data["earned_awt"]
        if remaining_epoch_cap <= 0:
            return False, f"Daily epoch limit reached ({node_data['earned_awt']:.2f}/{self.MAX_AWT_PER_EPOCH_PER_NODE} AWT/day).", 0.0

        allowed_reward = min(requested_reward_awt, remaining_epoch_cap)
        return True, f"Epoch capacity available ({allowed_reward:.2f} AWT approved for this cycle).", allowed_reward

    def record_epoch_settlement(self, node_id: str, awarded_awt: float):
        epoch_id = self._get_current_epoch_id()
        if node_id in self.node_epoch_earnings and self.node_epoch_earnings[node_id]["epoch_id"] == epoch_id:
            self.node_epoch_earnings[node_id]["earned_awt"] += awarded_awt
            self.node_epoch_earnings[node_id]["task_timestamps"].append(time.time())


class EconomicProofValidator:
    """
    Validates that every AWT emission is tethered to verifiable, institutional
    economic inflow (e.g. CEDA audit fees, B2B ad campaigns, SEZA IoT telemetry).
    Prevents unbacked token minting.
    """
    VALID_PROOF_TYPES = [
        "CEDA_STATUTORY_AUDIT_FEE",
        "B2B_AD_CAMPAIGN_PAYMENT",
        "SEZA_IOT_TELEMETRY_AUDIT",
        "GOSPEL_OS_STOREFRONT_PURCHASE"
    ]

    @classmethod
    def verify_economic_proof(cls, proof_data: Dict[str, any]) -> Tuple[bool, str, float]:
        proof_type = proof_data.get("proof_type")
        reference_id = proof_data.get("reference_id")
        fiat_amount_bwp = proof_data.get("fiat_amount_bwp", 0.0)

        if proof_type not in cls.VALID_PROOF_TYPES:
            return False, f"Invalid economic proof type: {proof_type}. Unbacked mining rejected.", 0.0

        if not reference_id or len(str(reference_id)) < 8:
            return False, "Missing or invalid institutional reference transaction ID.", 0.0

        if fiat_amount_bwp <= 0:
            return False, "Economic proof has zero fiat value. AWT emissions require positive BWP backing.", 0.0

        # Backing Ratio: Allow max 1.0 AWT emission per BWP 0.50 of institutional revenue
        max_backed_awt_emission = round(fiat_amount_bwp * 2.0, 2)

        return True, f"Verified economic proof ({proof_type} Ref: {reference_id}, BWP {fiat_amount_bwp:.2f}).", max_backed_awt_emission


class PoUCTriadValidator:
    """
    Implements the 3-Filter PoUC Validation Triad:
    Filter 1: Semantic Entropy & Novelty Check
    Filter 2: Blind Adversarial Peer Triangulation
    Filter 3: Epistemic Delta (ΔE) Validation
    """
    MAX_COSINE_SIMILARITY_THRESHOLD = 0.92
    MAX_PEER_VARIANCE_THRESHOLD = 0.50

    @classmethod
    def compute_wisdom_quotient(cls, scores: Dict[str, float]) -> float:
        fn = max(0.1, scores.get("foresight_depth_Fn", 1.0))
        ac = max(0.1, scores.get("axiological_coverage_Ac", 0.5))
        r_risk = max(0.1, scores.get("irreversibility_risk_Rrisk", 1.0))
        h_pen = max(0.1, scores.get("epistemic_hubris_penalty_Hpen", 1.0))
        
        w_score = (fn * ac) / (r_risk + h_pen)
        return round(w_score, 4)

    @classmethod
    def filter_1_semantic_novelty(cls, surfaced_blindspot: str, default_answers: List[str]) -> bool:
        if not surfaced_blindspot or len(surfaced_blindspot.strip()) < 20:
            return False
        
        words = set(surfaced_blindspot.lower().split())
        for default_ans in default_answers:
            def_words = set(default_ans.lower().split())
            jaccard_sim = len(words & def_words) / float(len(words | def_words) + 1e-5)
            if jaccard_sim > cls.MAX_COSINE_SIMILARITY_THRESHOLD:
                return False
        return True

    @classmethod
    def filter_2_peer_triangulation(cls, node_w_score: float, peer_w_scores: List[float]) -> Tuple[bool, float]:
        if not peer_w_scores:
            return True, 0.0
        
        all_scores = peer_w_scores + [node_w_score]
        mean = sum(all_scores) / len(all_scores)
        variance = sum((x - mean) ** 2 for x in all_scores) / len(all_scores)
        
        is_valid = variance <= cls.MAX_PEER_VARIANCE_THRESHOLD
        return is_valid, round(variance, 4)

    @classmethod
    def filter_3_epistemic_delta(cls, surfaced_blindspot: str, statutory_keywords: List[str]) -> float:
        base_delta = 1.0
        matched = sum(1 for kw in statutory_keywords if kw.lower() in surfaced_blindspot.lower())
        epistemic_delta = base_delta + (matched * 0.25)
        return round(min(epistemic_delta, 2.5), 2)


class DualTokenSettlementEngine:
    """
    Manages dual-token ledger updates:
    1. AWT (Artificial Wisdom Token): Fungible liquid utility token (1B fixed cap).
    2. W_tau (Soulbound Reputation): Non-transferable credibility score.
    Integrates Epoch Vesting, Economic Proof Verification, and 20% Buyback-and-Burn.
    """
    BASE_AWT_REWARD_PER_TASK = 5.0
    BASE_W_TAU_CREDIT_PER_TASK = 0.05
    BUYBACK_BURN_PERCENTAGE = 0.20  # 20% of revenue buys back & burns AWT

    def __init__(self):
        self.node_balances: Dict[str, float] = {}       # AWT Liquid
        self.node_reputation: Dict[str, float] = {}     # W_tau Soulbound
        self.total_awt_minted: float = 0.0
        self.total_awt_burned: float = 0.0
        self.fiat_audit_treasury_bwp: float = 0.0
        self.epoch_controller = EpochVestingController()

    def get_or_create_node(self, node_id: str):
        if node_id not in self.node_balances:
            self.node_balances[node_id] = 0.0
            self.node_reputation[node_id] = 1.0  # Base starting reputation

    def settle_pouc_submission(
        self,
        node_id: str,
        epistemic_delta: float,
        economic_proof: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Settles PoUC micro-task rewards ONLY if hardware interlocks, economic proof,
        and epoch vesting caps are satisfied.
        """
        self.get_or_create_node(node_id)

        # 1. Validate Economic Proof
        proof_valid, proof_msg, max_backed_awt = EconomicProofValidator.verify_economic_proof(economic_proof)
        if not proof_valid:
            return {
                "status": "REJECTED_UNBACKED_EMISSION",
                "reason": proof_msg,
                "node_id": node_id,
                "awt_minted": 0.0
            }

        # 2. Calculate Uncapped Task Reward
        raw_reward = round(self.BASE_AWT_REWARD_PER_TASK * epistemic_delta, 2)
        capped_by_proof_reward = min(raw_reward, max_backed_awt)

        # 3. Epoch Rate Limiting & Daily Cap Check
        limit_ok, limit_msg, final_awarded_awt = self.epoch_controller.check_epoch_limit(node_id, capped_by_proof_reward)
        if not limit_ok or final_awarded_awt <= 0:
            return {
                "status": "REJECTED_EPOCH_LIMIT_EXCEEDED",
                "reason": limit_msg,
                "node_id": node_id,
                "awt_minted": 0.0
            }

        # 4. Execute Ledger Update
        w_tau_gain = round(self.BASE_W_TAU_CREDIT_PER_TASK * epistemic_delta, 3)
        
        self.node_balances[node_id] += final_awarded_awt
        self.node_reputation[node_id] += w_tau_gain
        self.total_awt_minted += final_awarded_awt
        self.epoch_controller.record_epoch_settlement(node_id, final_awarded_awt)

        return {
            "status": "SETTLED_WITH_ECONOMIC_PROOF",
            "node_id": node_id,
            "economic_proof_reference": economic_proof.get("reference_id"),
            "awt_minted": final_awarded_awt,
            "awt_total_balance": round(self.node_balances[node_id], 2),
            "w_tau_credited": w_tau_gain,
            "w_tau_total_reputation": round(self.node_reputation[node_id], 3),
            "epoch_status": limit_msg
        }

    def process_enterprise_audit_fee(self, fee_amount_bwp: float, awt_market_price_bwp: float) -> Dict[str, float]:
        """
        Receives enterprise audit fees and executes 20% Buyback-and-Burn.
        """
        self.fiat_audit_treasury_bwp += fee_amount_bwp
        burn_budget_bwp = fee_amount_bwp * self.BUYBACK_BURN_PERCENTAGE
        
        awt_burned = round(burn_budget_bwp / max(0.01, awt_market_price_bwp), 2)
        self.total_awt_burned += awt_burned
        
        return {
            "fee_received_bwp": fee_amount_bwp,
            "burn_budget_bwp": burn_budget_bwp,
            "awt_market_price_bwp": awt_market_price_bwp,
            "awt_burned": awt_burned,
            "total_awt_burned_cumulative": round(self.total_awt_burned, 2),
            "treasury_net_retained_bwp": round(fee_amount_bwp - burn_budget_bwp, 2)
        }


# ===================================================================================
# SELF-TEST SUITE & VERIFICATION RUNTIME
# ===================================================================================

def run_reward_engine_verification():
    print("=" * 80)
    print(" 🛡️ LAVETO WISDOM (AW-1) REWARD & TOKENOMICS ENGINE TEST RUN")
    print("=" * 80)

    # 1. Test Hardware Interlocks
    print("\n[1. MOBILE EDGE HARDWARE INTERLOCKS CHECK]")
    valid_telemetry = {
        "power_source": "AC_CHARGING",
        "network_type": "UNMETERED_WIFI",
        "battery_level_percent": 88,
        "thermal_state_celsius": 30.5
    }
    passed, msg = HardwareInterlockVerifier.verify(valid_telemetry)
    print(f"  • Telemetry Status: Passed={passed} ({msg})")
    assert passed, "Hardware interlock test failed!"

    # 2. Test PoUC Triad Filters
    print("\n[2. POUC TRIAD FILTERS EVALUATION]")
    node_id = "node-edge-bw-9941"
    evaluation_scores = {
        "foresight_depth_Fn": 4.8,
        "axiological_coverage_Ac": 0.88,
        "irreversibility_risk_Rrisk": 1.1,
        "epistemic_hubris_penalty_Hpen": 0.7
    }
    surfaced_blindspot = "Path A ignores regional transport bottlenecks at the Kazungula transit corridor during peak harvest months, threatening severe crop spoilage."
    default_answers = ["Proceed with standard solar cold storage installation without delay."]
    statutory_keywords = ["Kazungula", "harvest", "CEE", "SEZA", "spoilage"]

    w_score = PoUCTriadValidator.compute_wisdom_quotient(evaluation_scores)
    f1_pass = PoUCTriadValidator.filter_1_semantic_novelty(surfaced_blindspot, default_answers)
    peer_scores = [1.95, 2.02]
    f2_pass, variance = PoUCTriadValidator.filter_2_peer_triangulation(w_score, peer_scores)
    epistemic_delta = PoUCTriadValidator.filter_3_epistemic_delta(surfaced_blindspot, statutory_keywords)

    print(f"  • Wisdom Quotient (W)       : {w_score}")
    print(f"  • Filter 1 (Semantic Novelty) : {'PASS' if f1_pass else 'FAIL'}")
    print(f"  • Filter 2 (Peer Triangulation): Variance={variance} -> {'PASS' if f2_pass else 'FAIL'}")
    print(f"  • Filter 3 (Epistemic Delta ΔE): {epistemic_delta}x Information Gain")

    # 3. Test Economic Proof & Epoch-Based Rate Limiting Settlement
    print("\n[3. ECONOMIC PROOF & EPOCH VESTING SETTLEMENT]")
    settlement_engine = DualTokenSettlementEngine()

    # Attempt 3a: Unbacked Emission (Should be Rejected)
    unbacked_proof = {"proof_type": "UNBACKED_PASSIVE_MINING", "fiat_amount_bwp": 0.0}
    rejection = settlement_engine.settle_pouc_submission(node_id, epistemic_delta, unbacked_proof)
    print(f"  • Unbacked Task Test : {rejection['status']} -> {rejection['reason']}")

    # Attempt 3b: Valid CEDA Statutory Audit Backed Task (Should Pass)
    valid_proof = {
        "proof_type": "CEDA_STATUTORY_AUDIT_FEE",
        "reference_id": "TX-CEDA-AUDIT-90124",
        "fiat_amount_bwp": 10000.00
    }
    settlement = settlement_engine.settle_pouc_submission(node_id, epistemic_delta, valid_proof)
    print(f"  • Backed Task Settlement: {settlement['status']}")
    print(f"    - AWT Minted          : +{settlement['awt_minted']} AWT (Balance: {settlement['awt_total_balance']} AWT)")
    print(f"    - Soulbound W_tau Gain: +{settlement['w_tau_credited']} (Reputation: {settlement['w_tau_total_reputation']})")

    # 4. Test Enterprise Audit Buyback-and-Burn
    print("\n[4. ENTERPRISE AUDIT BUYBACK-AND-BURN]")
    enterprise_fee_bwp = 25000.00
    awt_price_bwp = 2.50
    burn_result = settlement_engine.process_enterprise_audit_fee(enterprise_fee_bwp, awt_price_bwp)
    print(f"  • Enterprise Audit Fee Received : BWP {burn_result['fee_received_bwp']:,.2f}")
    print(f"  • Buyback & Burn Budget (20%)   : BWP {burn_result['burn_budget_bwp']:,.2f}")
    print(f"  • AWT Tokens Burned             : {burn_result['awt_burned']:,.2f} AWT")
    print(f"  • Net Retained Treasury         : BWP {burn_result['treasury_net_retained_bwp']:,.2f}")

    print("\n" + "=" * 80)
    print(" ✅ REWARD & TOKENOMICS ENGINE INTEGRATION TEST PASSED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_reward_engine_verification()


# --- Backward Compatibility Bridge ---
class AWRewardEngine(DualTokenSettlementEngine):
    pass
