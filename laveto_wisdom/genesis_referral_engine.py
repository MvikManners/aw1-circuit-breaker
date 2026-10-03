"""
===================================================================================
LAVETO WISDOM (AW-1) — GENESIS NODE REFERRAL & SQUAD ROYALTY TRACKING ENGINE
===================================================================================
Module: genesis_referral_engine.py
Purpose: Codifies Node 0 Genesis referral link generation, downstream squad tree tracking,
         dual +10 AWT sign-up activation bonuses, 5% perpetual mining royalty overrides,
         and localized social copy generation (English & Setswana) for launch.
===================================================================================
"""

import json
import hashlib
import time
from datetime import datetime, timezone

class GenesisReferralEngine:
    def __init__(self, genesis_owner="Genesis Pioneer (Node 0)"):
        self.genesis_owner = genesis_owner
        self.nodes = {}
        self.referral_tree = {} # parent_id -> list of child_ids
        self.total_network_awt_minted = 0.0
        self.total_royalties_paid_to_genesis = 0.0
        
        # Initialize Node 0 (Genesis Node)
        self.genesis_id = "node-bw-genesis-000"
        self.genesis_ref_code = "BW-GENESIS-APEX"
        self.nodes[self.genesis_id] = {
            "node_id": self.genesis_id,
            "owner": self.genesis_owner,
            "ref_code": self.genesis_ref_code,
            "parent_id": None,
            "balance_awt": 0.0,
            "reputation_w_tau": 5.0, # Initial seed reputation
            "squad_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        self.referral_tree[self.genesis_id] = []

    def generate_referral_code(self, node_id):
        hash_digest = hashlib.sha256(f"{node_id}-{time.time()}".encode()).hexdigest()[:6].upper()
        return f"BW-LAVETO-{hash_digest}"

    def onboard_new_node(self, owner_name, referrer_code=None):
        """
        Onboards a new citizen node into the referral tree.
        Triggers the +10 AWT Dual Activation Bonus for both referrer and new node.
        """
        node_num = len(self.nodes)
        new_node_id = f"node-bw-citizen-{node_num:03d}"
        new_ref_code = self.generate_referral_code(new_node_id)
        
        # Find referrer node ID
        referrer_id = None
        if referrer_code:
            for nid, data in self.nodes.items():
                if data["ref_code"] == referrer_code:
                    referrer_id = nid
                    break

        if not referrer_id:
            referrer_id = self.genesis_id # Default fallback to Genesis Node

        # Create new node
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
        self.referral_tree[referrer_id].append(new_node_id)
        self.nodes[referrer_id]["squad_count"] += 1

        # DUAL ACTIVATION BONUS (+10 AWT EACH)
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
            "activation_bonus_credited": f"+{activation_bonus} AWT to both inviter and new node"
        }

    def process_pouc_evaluation_reward(self, worker_node_id, base_reward_awt=20.0):
        """
        Processes PoUC verification task completed by worker node.
        Calculates and credits 5% perpetual mining royalty to Genesis Node (Node 0).
        """
        if worker_node_id not in self.nodes:
            raise ValueError(f"Node {worker_node_id} not found.")

        # 1. Credit base reward to worker node
        self.nodes[worker_node_id]["balance_awt"] += base_reward_awt
        self.nodes[worker_node_id]["reputation_w_tau"] += 0.05
        self.total_network_awt_minted += base_reward_awt

        # 2. Calculate 5% Royalty Override for Genesis Node (Node 0)
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
                "squad_size_direct": len(self.referral_tree[self.genesis_id]),
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
        """Generates localized launch text templates for WhatsApp, Facebook, and X."""
        ref_code = self.genesis_ref_code
        link = f"https://p20.laveto.net/join?ref={ref_code}"

        english_text = (
            f"🚀 I just launched my Genesis Verification Node on p20.laveto.net!\n\n"
            f"Earn BWP daily while your phone charges overnight on Wi-Fi (0% mobile data used).\n"
            f"💰 Click my Genesis link to claim your instant +10 AWT activation bonus:\n"
            f"👉 {link}\n\n"
            f"Cash out directly to Orange Money & Mascom MyZaka! 🇧🇼 #LavetoWisdom #BotswanaDigitalWealth"
        )

        setswana_text = (
            f"🇧🇼 Tsaya taolo ya madi a gago ka p20.laveto.net!\n\n"
            f"Bula verification node ya gago o amogele madi a BWP letsatsi le letsatsi mogala wa gago o le mo chajeng le mo Wi-Fi.\n"
            f"🎁 Kgotla link ya me ya Genesis o amogele bonus ya mahala ya +10 AWT ka yone nako e:\n"
            f"👉 {link}\n\n"
            f"Amogela madi a gago thwi mo Orange Money kapa Mascom MyZaka!"
        )

        return {"english_copy": english_text, "setswana_copy": setswana_text}