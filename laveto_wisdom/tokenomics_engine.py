"""
===============================================================================
LAVETO WISDOM (AW-1) — TOKENOMICS GOVERNANCE & SETTLEMENT ENGINE
===============================================================================
Module: tokenomics_engine.py
Purpose: Production-grade tokenomics implementation governing supply caps,
         Epistemic Delta reward scaling, 20% enterprise buyback-and-burn,
         5% referral overrides, and dual-token (AWT / W_tau) SQLite settlement.
===============================================================================
"""

import sqlite3
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, Tuple

DB_PATH = "/home/LavetoLab/lvt_backend/tokenomics_ledger.db"

class TokenomicsEngine:
    """
    Core Tokenomics Execution Engine for Laveto Wisdom (AW-1).
    Manages 1B AWT fixed supply, automated 20% enterprise buyback-and-burn,
    Proof of Useful Contribution (PoUC) payouts, and W_tau Soulbound Reputation.
    """

    MAX_AWT_SUPPLY = 1_000_000_000.0
    ALLOCATION_POUC_NODES = 0.45
    ALLOCATION_TREASURY = 0.20
    ALLOCATION_REFERRALS = 0.15
    ALLOCATION_OFFRAMP_LIQUIDITY = 0.10
    ALLOCATION_CORE_TEAM = 0.10

    FEE_BUYBACK_BURN_RATIO = 0.20
    FEE_CITIZEN_REWARD_RATIO = 0.45
    FEE_TREASURY_RATIO = 0.20
    FEE_REFERRAL_POOL_RATIO = 0.15

    DEFAULT_AWT_BWP_SPOT_RATE = 2.50
    REFERRAL_OVERRIDE_PERCENT = 0.05
    REFERRAL_ACTIVATION_BONUS = 10.0

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS supply_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_minted REAL DEFAULT 0.0,
                total_burned REAL DEFAULT 0.0,
                circulating_supply REAL DEFAULT 1000000000.0,
                treasury_bwp_reserve REAL DEFAULT 0.0
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wallets (
                address TEXT PRIMARY KEY,
                awt_liquid REAL DEFAULT 0.0,
                w_tau_reputation REAL DEFAULT 1.0,
                referred_by TEXT,
                total_earned_awt REAL DEFAULT 0.0,
                total_referral_awt REAL DEFAULT 0.0,
                created_at TEXT NOT NULL
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS burn_transactions (
                tx_hash TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                audit_id TEXT NOT NULL,
                fiat_fee_bwp REAL NOT NULL,
                bwp_burned REAL NOT NULL,
                awt_burned REAL NOT NULL,
                spot_rate_bwp REAL NOT NULL
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS node_payouts (
                payout_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                node_address TEXT NOT NULL,
                task_id TEXT NOT NULL,
                base_awt REAL NOT NULL,
                epistemic_delta REAL NOT NULL,
                final_awt REAL NOT NULL,
                w_tau_credited REAL NOT NULL,
                referral_royalty_awt REAL DEFAULT 0.0
            );
        """)

        cursor.execute("SELECT COUNT(*) FROM supply_ledger;")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO supply_ledger (timestamp, total_minted, total_burned, circulating_supply, treasury_bwp_reserve)
                VALUES (?, 0.0, 0.0, ?, 500000.0);
            """, (self._now_iso(), self.MAX_AWT_SUPPLY))

        conn.commit()
        conn.close()

    def get_or_create_wallet(self, address: str, referred_by: str = None) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT address, awt_liquid, w_tau_reputation, referred_by, total_earned_awt, total_referral_awt FROM wallets WHERE address = ?;", (address,))
        row = cursor.fetchone()

        if not row:
            now_str = self._now_iso()
            cursor.execute("""
                INSERT INTO wallets (address, awt_liquid, w_tau_reputation, referred_by, total_earned_awt, total_referral_awt, created_at)
                VALUES (?, 0.0, 1.0, ?, 0.0, 0.0, ?);
            """, (address, referred_by, now_str))
            
            if referred_by:
                cursor.execute("UPDATE wallets SET awt_liquid = awt_liquid + ?, total_earned_awt = total_earned_awt + ? WHERE address = ?;", 
                               (self.REFERRAL_ACTIVATION_BONUS, self.REFERRAL_ACTIVATION_BONUS, address))
                cursor.execute("UPDATE wallets SET awt_liquid = awt_liquid + ?, total_referral_awt = total_referral_awt + ? WHERE address = ?;", 
                               (self.REFERRAL_ACTIVATION_BONUS, self.REFERRAL_ACTIVATION_BONUS, referred_by))

            conn.commit()
            cursor.execute("SELECT address, awt_liquid, w_tau_reputation, referred_by, total_earned_awt, total_referral_awt FROM wallets WHERE address = ?;", (address,))
            row = cursor.fetchone()

        conn.close()
        return {
            "address": row[0],
            "awt_liquid": row[1],
            "w_tau_reputation": row[2],
            "referred_by": row[3],
            "total_earned_awt": row[4],
            "total_referral_awt": row[5]
        }

    def process_enterprise_audit_fee(self, audit_id: str, fee_bwp: float, spot_rate_bwp: float = DEFAULT_AWT_BWP_SPOT_RATE) -> Dict[str, Any]:
        bwp_burned = fee_bwp * self.FEE_BUYBACK_BURN_RATIO
        awt_burned = bwp_burned / spot_rate_bwp
        bwp_citizen_pool = fee_bwp * self.FEE_CITIZEN_REWARD_RATIO
        bwp_treasury = fee_bwp * self.FEE_TREASURY_RATIO

        tx_raw = f"{audit_id}:{fee_bwp}:{awt_burned}:{self._now_iso()}"
        tx_hash = "0x" + hashlib.sha256(tx_raw.encode()).hexdigest()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO burn_transactions (tx_hash, timestamp, audit_id, fiat_fee_bwp, bwp_burned, awt_burned, spot_rate_bwp)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (tx_hash, self._now_iso(), audit_id, fee_bwp, bwp_burned, awt_burned, spot_rate_bwp))

        cursor.execute("""
            UPDATE supply_ledger 
            SET total_burned = total_burned + ?, 
                circulating_supply = circulating_supply - ?, 
                treasury_bwp_reserve = treasury_bwp_reserve + ?;
        """, (awt_burned, awt_burned, bwp_treasury))

        conn.commit()
        conn.close()

        return {
            "status": "BURN_COMPLETED",
            "tx_hash": tx_hash,
            "audit_id": audit_id,
            "gross_fee_bwp": fee_bwp,
            "bwp_burned": bwp_burned,
            "awt_burned": awt_burned,
            "bwp_citizen_pool": bwp_citizen_pool,
            "bwp_treasury_added": bwp_treasury,
            "spot_rate_bwp": spot_rate_bwp
        }

    def settle_node_payout(self, node_address: str, task_id: str, base_awt: float = 10.0, epistemic_delta: float = 1.25) -> Dict[str, Any]:
        wallet = self.get_or_create_wallet(node_address)
        final_awt = base_awt * epistemic_delta
        w_tau_gain = 0.05 * epistemic_delta

        referred_by = wallet.get("referred_by")
        referral_royalty = 0.0

        payout_id = "pay_" + hashlib.sha256(f"{node_address}:{task_id}:{self._now_iso()}".encode()).hexdigest()[:12]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE wallets 
            SET awt_liquid = awt_liquid + ?, 
                w_tau_reputation = w_tau_reputation + ?, 
                total_earned_awt = total_earned_awt + ?
            WHERE address = ?;
        """, (final_awt, w_tau_gain, final_awt, node_address))

        if referred_by:
            referral_royalty = final_awt * self.REFERRAL_OVERRIDE_PERCENT
            cursor.execute("""
                UPDATE wallets 
                SET awt_liquid = awt_liquid + ?, 
                    total_referral_awt = total_referral_awt + ? 
                WHERE address = ?;
            """, (referral_royalty, referral_royalty, referred_by))

        cursor.execute("""
            INSERT INTO node_payouts (payout_id, timestamp, node_address, task_id, base_awt, epistemic_delta, final_awt, w_tau_credited, referral_royalty_awt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (payout_id, self._now_iso(), node_address, task_id, base_awt, epistemic_delta, final_awt, w_tau_gain, referral_royalty))

        conn.commit()
        conn.close()

        updated_wallet = self.get_or_create_wallet(node_address)

        return {
            "payout_id": payout_id,
            "node_address": node_address,
            "task_id": task_id,
            "final_awt_earned": final_awt,
            "w_tau_credited": w_tau_gain,
            "referral_royalty_dispatched": referral_royalty,
            "referred_by": referred_by,
            "updated_wallet": updated_wallet
        }

    def get_tokenomics_summary(self) -> Dict[str, Any]:
        import sqlite3

        canonical_db = '/home/LavetoLab/lvt_backend/lvt_database.db'
        live_pouc_minted = 0.0
        total_settled_tasks = 0

        # 1. Fetch live PoUC settlements from awt_ledger
        try:
            conn_ledger = sqlite3.connect(canonical_db, timeout=15.0)
            cur_pouc = conn_ledger.cursor()
            pouc_row = cur_pouc.execute("SELECT COALESCE(SUM(awt_minted), 0.0), COUNT(*) FROM awt_ledger WHERE status = 'MINTED';").fetchone()
            if pouc_row:
                live_pouc_minted = float(pouc_row[0])
                total_settled_tasks = int(pouc_row[1])
            conn_ledger.close()
        except Exception as e:
            import sys
            sys.stderr.write(f"[LEDGER_QUERY_ERROR] {type(e).__name__}: {e}\n")

        # 2. Fetch baseline supply figures
        base_circulating = 0.0
        burned = 0.0
        treasury = 500000.0
        for s_db in [canonical_db, self.db_path]:
            try:
                conn_s = sqlite3.connect(s_db, timeout=15.0)
                cur_s = conn_s.cursor()
                cur_s.execute("SELECT total_minted, total_burned, circulating_supply, treasury_bwp_reserve FROM supply_ledger ORDER BY id DESC LIMIT 1;")
                row = cur_s.fetchone()
                if row:
                    burned = float(row[1]) if row[1] is not None else 0.0
                    base_circulating = float(row[2]) if row[2] is not None else 0.0
                    treasury = float(row[3]) if row[3] is not None else 500000.0
                    conn_s.close()
                    break
                conn_s.close()
            except Exception:
                pass

        return {
            "max_awt_supply": self.MAX_AWT_SUPPLY,
            "total_burned_awt": burned,
            "circulating_supply_awt": round(base_circulating + live_pouc_minted, 4),
            "pouc_minted_awt": round(live_pouc_minted, 4),
            "total_pouc_settlements": total_settled_tasks,
            "treasury_bwp_reserve": treasury,
            "spot_rate_bwp": self.DEFAULT_AWT_BWP_SPOT_RATE
        }