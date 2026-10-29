"""
Laveto Wisdom AW-1 — Proof of Useful Contribution (PoUC) Consensus Engine.
Enforces mobile/desktop hardware interlocks, 3-Filter Triad validation,
and Dual-Token (AWT + W_tau) settlement.
"""
import math
import json
import sqlite3
import hashlib
from datetime import datetime

DB_PATH = "/home/LavetoLab/lvt_backend/lvt_database.db"

class HardwareInterlock:
    @staticmethod
    def verify(telemetry: dict) -> tuple[bool, str]:
        power = telemetry.get("power_source", "")
        net = telemetry.get("network_type", "")
        batt = telemetry.get("battery_level_percent", 0)
        temp = telemetry.get("thermal_state_celsius", 100.0)
        is_desktop = telemetry.get("device_class", "MOBILE").upper() == "DESKTOP"

        if power != "AC_CHARGING":
            return False, "HARDWARE_INTERLOCK: Device must be connected to AC_CHARGING"
        if net != "UNMETERED_WIFI":
            return False, "HARDWARE_INTERLOCK: Unmetered Wi-Fi connection required (zero cellular data usage)"
        if batt < 80:
            return False, f"HARDWARE_INTERLOCK: Battery at {batt}% (minimum 80% required)"
        
        max_temp = 70.0 if is_desktop else 34.0
        if temp > max_temp:
            return False, f"HARDWARE_INTERLOCK: Thermal state {temp}°C exceeds ceiling {max_temp}°C"
        
        return True, "ALL_HARDWARE_INTERLOCKS_CLEARED"

def init_pouc_tables():
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pouc_node_registry (
                node_id TEXT PRIMARY KEY,
                device_class TEXT NOT NULL,
                w_tau_reputation REAL DEFAULT 1.0,
                awt_balance REAL DEFAULT 0.0,
                total_valid_contributions INTEGER DEFAULT 0,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pouc_gradient_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id TEXT UNIQUE NOT NULL,
                node_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                wisdom_quotient REAL NOT NULL,
                peer_variance REAL NOT NULL,
                surfaced_blindspot TEXT,
                epistemic_delta REAL NOT NULL,
                status TEXT NOT NULL,
                awt_minted REAL NOT NULL,
                w_tau_awarded REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    conn.close()

def process_pouc_submission(payload: dict) -> dict:
    init_pouc_tables()
    node_id = payload.get("node_id", "node-anonymous")
    device_class = payload.get("device_class", "MOBILE")
    telemetry = payload.get("telemetry", {})
    
    # 1. Gate Check: Hardware Interlock
    cleared, reason = HardwareInterlock.verify(telemetry)
    if not cleared:
        return {"status": "THROTTLED_HARDWARE_INTERLOCK", "message": reason, "rewards": None}

    # 2. Triad Filter Validation
    vector = payload.get("evaluation_vector", {})
    fn = float(vector.get("foresight_depth_Fn", 3.0))
    ac = float(vector.get("axiological_coverage_Ac", 0.5))
    r_risk = float(vector.get("irreversibility_risk_Rrisk", 1.5))
    h_pen = float(vector.get("epistemic_hubris_penalty_Hpen", 0.5))
    
    computed_w = round((fn * ac) / (r_risk + h_pen), 2)
    blindspot = payload.get("surfaced_blindspot", "").strip()

    # Filter 1: Novelty / Anti-farming check
    if len(blindspot) < 15:
        return {"status": "REJECTED_FILTER_1_LOW_ENTROPY", "message": "Evaluation lacked novel epistemic blindspot depth.", "rewards": None}

    # Filter 2: Blind Adversarial Peer Triangulation
    peer_scores = payload.get("peer_scores", [computed_w, computed_w])
    all_scores = peer_scores + [computed_w]
    mean = sum(all_scores) / len(all_scores)
    variance = round(sum((x - mean) ** 2 for x in all_scores) / len(all_scores), 3)

    if variance > 0.50:
        return {"status": "REJECTED_FILTER_2_HIGH_VARIANCE", "message": f"Peer variance {variance} exceeds 0.50 threshold.", "rewards": None}

    # Filter 3: Epistemic Delta Reward
    epistemic_delta = 1.25 if ("kazungula" in blindspot.lower() or "cee" in blindspot.lower() or "water" in blindspot.lower()) else 1.0
    awt_minted = round(10.0 * epistemic_delta, 1)
    w_tau_gain = 0.05

    sub_id = f"POUC-{hashlib.sha256(f'{node_id}:{datetime.utcnow()}'.encode('utf-8')).hexdigest()[:10].upper()}"

    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    with conn:
        conn.execute("""
            INSERT OR IGNORE INTO pouc_node_registry (node_id, device_class) VALUES (?, ?)
        """, (node_id, device_class))
        
        conn.execute("""
            UPDATE pouc_node_registry 
            SET w_tau_reputation = ROUND(w_tau_reputation + ?, 3),
                awt_balance = ROUND(awt_balance + ?, 2),
                total_valid_contributions = total_valid_contributions + 1,
                last_active = CURRENT_TIMESTAMP
            WHERE node_id = ?
        """, (w_tau_gain, awt_minted, node_id))

        conn.execute("""
            INSERT INTO pouc_gradient_submissions
            (submission_id, node_id, task_id, wisdom_quotient, peer_variance, surfaced_blindspot, epistemic_delta, status, awt_minted, w_tau_awarded)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'VALIDATED_AND_MINTED', ?, ?)
        """, (sub_id, node_id, payload.get("task_id", "TASK-GEN-01"), computed_w, variance, blindspot, epistemic_delta, awt_minted, w_tau_gain))
        
        updated_node = dict(conn.execute("SELECT * FROM pouc_node_registry WHERE node_id = ?", (node_id,)).fetchone())
    conn.close()

    return {
        "status": "VALIDATED_AND_MINTED",
        "submission_id": sub_id,
        "computed_wisdom_quotient": computed_w,
        "peer_variance": variance,
        "rewards": {
            "awt_minted": awt_minted,
            "w_tau_reputation_gain": w_tau_gain
        },
        "node_balance": updated_node
    }
