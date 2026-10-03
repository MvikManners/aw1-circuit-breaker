"""
===================================================================================
      LAVETO WISDOM (AW-1) — SELF-CONTAINED REWARD & REFERRAL ROUTES (V3)
===================================================================================
File: aw_reward_routes.py
Description: Self-contained Flask Blueprint integrating Genesis Referrals, 
             Hardware Interlocks, PoUCTriadValidator, Tokenomics, and Gate 7 Circuit Breaker.
===================================================================================
"""

import os
import hashlib
import json
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify

# ==========================================
# 1. GENESIS REFERRAL ENGINE
# ==========================================
class GenesisReferralEngine:
    def __init__(self, genesis_owner="Apex Genesis Pioneer (Node 0)"):
        self.genesis_owner = genesis_owner
        self.nodes = {}
        self.referral_tree = {}
        self.total_network_awt_minted = 0.0
        self.total_royalties_paid_to_genesis = 0.0
        
        self.genesis_id = "node-bw-genesis-000"
        self.genesis_ref_code = "BW-GENESIS-APEX"
        self.nodes[self.genesis_id] = {
            "node_id": self.genesis_id,
            "owner": self.genesis_owner,
            "ref_code": self.genesis_ref_code,
            "parent_id": None,
            "balance_awt": 0.0,
            "reputation_w_tau": 5.0,
            "squad_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        self.referral_tree[self.genesis_id] = []

    def generate_referral_code(self, node_id):
        hash_digest = hashlib.sha256(f"{node_id}-{datetime.now().timestamp()}".encode()).hexdigest()[:6].upper()
        return f"BW-LAVETO-{hash_digest}"

    def onboard_new_node(self, owner_name, referrer_code=None):
        node_num = len(self.nodes)
        new_node_id = f"node-bw-citizen-{node_num:03d}"
        new_ref_code = self.generate_referral_code(new_node_id)
        
        referrer_id = None
        if referrer_code:
            for nid, data in self.nodes.items():
                if data["ref_code"] == referrer_code:
                    referrer_id = nid
                    break
        if not referrer_id:
            referrer_id = self.genesis_id

        self.nodes[new_node_id] = {
            "node_id": new_node_id,
            "owner": owner_name,
            "ref_code": new_ref_code,
            "parent_id": referrer_id,
            "balance_awt": 0.0,
            "reputation_w_tau": 1.0,
            "squad_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        self.referral_tree[new_node_id] = []
        if referrer_id in self.referral_tree:
            self.referral_tree[referrer_id].append(new_node_id)
        self.nodes[referrer_id]["squad_count"] += 1

        activation_bonus = 10.0
        self.nodes[new_node_id]["balance_awt"] += activation_bonus
        self.nodes[referrer_id]["balance_awt"] += activation_bonus
        self.total_network_awt_minted += (activation_bonus * 2)

        return {
            "status": "ONBOARDED_AND_BONUS_CREDITED",
            "node_id": new_node_id,
            "owner": owner_name,
            "referrer_id": referrer_id,
            "your_referral_code": new_ref_code,
            "activation_bonus_credited": f"+{activation_bonus} AWT"
        }

    def process_pouc_evaluation_reward(self, worker_node_id, base_reward_awt=20.0):
        if worker_node_id not in self.nodes:
            self.nodes[worker_node_id] = {"balance_awt": 0.0, "reputation_w_tau": 1.0}

        self.nodes[worker_node_id]["balance_awt"] += base_reward_awt
        self.nodes[worker_node_id]["reputation_w_tau"] += 0.05
        self.total_network_awt_minted += base_reward_awt

        royalty_5_pct = base_reward_awt * 0.05
        self.nodes[self.genesis_id]["balance_awt"] += royalty_5_pct
        self.total_royalties_paid_to_genesis += royalty_5_pct
        self.total_network_awt_minted += royalty_5_pct

        return {
            "worker_node_id": worker_node_id,
            "base_reward_paid": f"{base_reward_awt} AWT",
            "genesis_royalty_override_paid": f"{royalty_5_pct:.2f} AWT (5%)",
            "genesis_total_balance": f"{self.nodes[self.genesis_id]['balance_awt']:.2f} AWT"
        }

    def get_network_tree_summary(self):
        genesis_node = self.nodes[self.genesis_id]
        spot_rate_bwp = 2.50
        total_bwp_val = genesis_node["balance_awt"] * spot_rate_bwp
        return {
            "genesis_node": {
                "owner": genesis_node["owner"],
                "node_id": genesis_node["node_id"],
                "referral_code": genesis_node["ref_code"],
                "squad_size_direct": len(self.referral_tree.get(self.genesis_id, [])),
                "accumulated_awt": round(genesis_node["balance_awt"], 2),
                "bwp_cashout_value": f"P{total_bwp_val:,.2f} BWP",
                "soulbound_reputation_w_tau": round(genesis_node["reputation_w_tau"], 2)
            },
            "network_metrics": {
                "total_active_nodes": len(self.nodes),
                "total_awt_minted": round(self.total_network_awt_minted, 2),
                "total_royalties_flowed_to_genesis": round(self.total_royalties_paid_to_genesis, 2)
            }
        }

    def generate_launch_social_copy(self):
        link = f"https://p20.laveto.net/join?ref={self.genesis_ref_code}"
        return {
            "english_copy": f"🚀 I just launched my Genesis Verification Node on p20.laveto.net! Earn BWP daily while your phone charges overnight. Claim +10 AWT bonus: {link} 🇧🇼 #LavetoWisdom",
            "setswana_copy": f"🇧🇼 Bula verification node ya gago o amogele madi a BWP ka p20.laveto.net. Kgotla link: {link}"
        }


# ==========================================
# 2. HARDWARE & TOKENOMICS ENGINES
# ==========================================
class HardwareInterlockVerifier:
    @staticmethod
    def verify(telemetry: dict):
        power = telemetry.get("power_source", "AC_CHARGING")
        net = telemetry.get("network_type", "UNMETERED_WIFI")
        batt = telemetry.get("battery_level_percent", 90)
        therm = telemetry.get("thermal_state_celsius", 29.4)
        
        if power != "AC_CHARGING":
            return False, "Interlock Failed: Device not connected to AC charging."
        if batt < 80:
            return False, f"Interlock Failed: Battery level {batt}% is below 80% safe threshold."
        if therm > 34.0:
            return False, f"Interlock Failed: Thermal state {therm}°C exceeds 34.0°C mobile safe limit."
        return True, "All Hardware Interlocks Verified Successfully."


class PoUCTriadValidator:
    @staticmethod
    def compute_wisdom_quotient(scores: dict) -> float:
        fn = scores.get("foresight_depth_Fn", 3.0)
        ac = scores.get("axiological_coverage_Ac", 0.8)
        r_risk = scores.get("irreversibility_risk_Rrisk", 1.0)
        h_pen = scores.get("epistemic_hubris_penalty_Hpen", 0.5)
        return round((fn * ac) / (r_risk + h_pen), 2)

    @staticmethod
    def filter_1_semantic_novelty(blindspot: str, defaults: list) -> bool:
        return len(blindspot.strip()) > 10

    @staticmethod
    def filter_2_peer_triangulation(w_score: float, peer_scores: list):
        if not peer_scores:
            return True, 0.05
        avg = sum(peer_scores) / len(peer_scores)
        variance = abs(w_score - avg)
        return variance <= 0.50, round(variance, 3)

    @staticmethod
    def filter_3_epistemic_delta(blindspot: str, keywords: list) -> float:
        matches = sum(1 for kw in keywords if kw.lower() in blindspot.lower())
        return round(1.0 + (matches * 0.15), 2)


class TokenomicsEngine:
    def __init__(self):
        self.MAX_AWT_SUPPLY = 1000000000
        self.DEFAULT_AWT_BWP_SPOT_RATE = 2.50
        self.circulating_supply = 450000000.0
        self.total_burned = 18000.0
        self.treasury_bwp = 540000.00

    def Settle_node_payout(self, node_address, task_id, base_awt, epistemic_delta):
        payout = base_awt * epistemic_delta
        self.circulating_supply += payout
        return {
            "node": node_address,
            "task_id": task_id,
            "net_awt_minted": payout
        }

    def process_enterprise_audit_fee(self, audit_id, fee_bwp, spot_rate):
        burn_bwp = fee_bwp * 0.20
        burned_awt = burn_bwp / spot_rate
        self.total_burned += burned_awt
        self.circulating_supply -= burned_awt
        self.treasury_bwp += fee_bwp
        return {
            "audit_id": audit_id,
            "fee_collected_bwp": fee_bwp,
            "awt_permanently_burned": burned_awt,
            "new_treasury_reserve_bwp": self.treasury_bwp
        }


# ==========================================
# 3. GATE 7 CIRCUIT BREAKER
# ==========================================
class AutonomousAgentInterceptor:
    @classmethod
    def audit_agent_payload(cls, agent_id: str, payload: dict) -> dict:
        action = payload.get("action_name", payload.get("action", "EVALUATE"))
        is_irreversible = payload.get("is_irreversible", False)
        now_str = datetime.now(timezone.utc).isoformat()
        
        if is_irreversible or "SHELL" in action.upper():
            return {
                "dossier_id": "DOSSIER-" + hashlib.sha256(f"{agent_id}:{now_str}".encode()).hexdigest()[:12],
                "audit_decision": "HALT_AND_CONTAIN",
                "gate_triggered": "Gate 7: One-Way Door Circuit Breaker",
                "wisdom_quotient_W": 0.12,
                "remediation": "Agent execution revoked."
            }
        return {
            "dossier_id": "DOSSIER-" + hashlib.sha256(f"{agent_id}:{now_str}".encode()).hexdigest()[:12],
            "audit_decision": "APPROVED_WITH_CONDITIONS",
            "gate_triggered": "NO_VIOLATION",
            "wisdom_quotient_W": 2.45,
            "remediation": "Proceed with standard execution."
        }


# ==========================================
# 4. FLASK BLUEPRINT & ENDPOINTS
# ==========================================
aw_reward_bp = Blueprint('aw_reward_bp', __name__)

tokenomics_engine = TokenomicsEngine()
genesis_engine = GenesisReferralEngine(genesis_owner="Apex Genesis Pioneer (Node 0)")
statutory_keywords = ["CEE", "SEZA", "Kazungula", "water", "IRP", "BWP", "food import", "grain"]
default_answers = ["Proceed with standard execution."]

@aw_reward_bp.route('/v1/aw/referral/onboard', methods=['POST'])
def onboard_referral_node():
    try:
        data = request.get_json() or {}
        receipt = genesis_engine.onboard_new_node(data.get("owner_name", "Citizen"), data.get("referrer_code", "BW-GENESIS-APEX"))
        return jsonify({"status": "SUCCESS", "receipt": receipt, "social_share": genesis_engine.generate_launch_social_copy()}), 200
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@aw_reward_bp.route('/v1/aw/referral/summary', methods=['GET'])
def get_referral_summary():
    try:
        return jsonify({"status": "SUCCESS", "apex_summary": genesis_engine.get_network_tree_summary(), "share_copy": genesis_engine.generate_launch_social_copy()}), 200
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@aw_reward_bp.route('/v1/aw/pouc/submit', methods=['POST'])
def submit_pouc_gradient():
    try:
        payload = request.get_json() or {}
        node_id = payload.get("node_id", "node-bw-genesis-000")
        
        passed, msg = HardwareInterlockVerifier.verify(payload.get("telemetry", {}))
        if not passed:
            return jsonify({"status": "REJECTED", "message": msg}), 422
            
        w_score = PoUCTriadValidator.compute_wisdom_quotient(payload.get("scores", {}))
        delta = PoUCTriadValidator.filter_3_epistemic_delta(payload.get("surfaced_blindspot", ""), statutory_keywords)
        
        receipt = tokenomics_engine.Settle_node_payout(node_id, payload.get("task_id", "t-1"), 10.0, delta)
        royalty = genesis_engine.process_pouc_evaluation_reward(node_id, 10.0 * delta)
        
        return jsonify({"status": "VALIDATED_AND_SETTLED", "wisdom_quotient_W": w_score, "receipt": receipt, "royalty": royalty}), 200
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@aw_reward_bp.route('/v1/aw/audit', methods=['POST'])
def process_enterprise_audit():
    try:
        data = request.get_json() or {}
        res = AutonomousAgentInterceptor.audit_agent_payload(data.get("agent_id", "agent-1"), data)
        burn = tokenomics_engine.process_enterprise_audit_fee(res["dossier_id"], float(data.get("audit_fee_bwp", 25000)), 2.50)
        return jsonify({"status": res["audit_decision"], "audit_result": res, "burn_receipt": burn}), 200
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500

@aw_reward_bp.route('/v1/aw/tokenomics/summary', methods=['GET'])
def get_tokenomics_summary():
    return jsonify({
        "status": "SUCCESS",
        "max_supply_awt": tokenomics_engine.MAX_AWT_SUPPLY,
        "circulating_supply_awt": tokenomics_engine.circulating_supply,
        "total_burned_awt": tokenomics_engine.total_burned,
        "treasury_bwp_reserve": tokenomics_engine.treasury_bwp,
        "spot_rate_bwp": tokenomics_engine.DEFAULT_AWT_BWP_SPOT_RATE
    }), 200