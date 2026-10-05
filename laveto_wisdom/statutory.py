import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone

DB_PATH = '/home/LavetoLab/lvt_database.db'

class StatutoryLensEngine:
    """
    Evaluates real-time statutory compliance (Botswana DPA 2018)
    and enforces Bank of Botswana / Laveto Pay fiduciary trust solvency.
    """

    # Botswana Omang Pattern: 9 digits, typically 5th digit denotes gender (1 or 2)
    OMANG_REGEX = re.compile(r'\b\d{4}[12]\d{4}\b|\b\d{9}\b')
    # Standard PAN (Payment Card) Pattern
    PAN_REGEX = re.compile(r'\b(?:\d{4}[- ]?){3}\d{4}\b')

    @classmethod
    def evaluate_payload_sovereignty(cls, payload: str):
        """
        Inspects string payload for raw PII violations under Botswana DPA.
        """
        violations = []
        if cls.OMANG_REGEX.search(payload):
            violations.append("DPA_OMANG_UNMASKED")
        if cls.PAN_REGEX.search(payload):
            violations.append("PCI_PAN_UNMASKED")
        
        # Check cross-border data routing markers
        lowered = payload.lower()
        if "export_jurisdiction" in lowered and "bw" not in lowered:
            violations.append("CROSS_BORDER_SOVEREIGNTY_BREACH")

        return violations

    @classmethod
    def verify_fiduciary_solvency(cls, agent_id: str, cost_bwp: float):
        """
        Ensures agent has sufficient escrow balance and is within daily velocity limits.
        """
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        row = c.execute(
            "SELECT account_id, balance_bwp, daily_velocity_limit_bwp, daily_spent_bwp, status FROM agent_fiduciary_accounts WHERE agent_id = ?",
            (agent_id,)
        ).fetchone()

        if not row:
            conn.close()
            return False, "NO_FIDUCIARY_ACCOUNT", 0.0

        acc_id, balance, vel_limit, spent, status = row

        if status != 'ACTIVE':
            conn.close()
            return False, "ACCOUNT_FROZEN", balance

        if cost_bwp > balance:
            conn.close()
            return False, f"INSOLVENT: required BWP {cost_bwp:.2f}, balance BWP {balance:.2f}", balance

        if (spent + cost_bwp) > vel_limit:
            conn.close()
            return False, f"VELOCITY_LIMIT_EXCEEDED: daily limit BWP {vel_limit:.2f}", balance

        # Atomic deduction
        now = datetime.now(timezone.utc).isoformat()
        c.execute("""
            UPDATE agent_fiduciary_accounts 
            SET balance_bwp = balance_bwp - ?, 
                daily_spent_bwp = daily_spent_bwp + ?,
                updated_at = ?
            WHERE agent_id = ?
        """, (cost_bwp, cost_bwp, now, agent_id))
        
        conn.commit()
        conn.close()
        return True, "SOLVENT", balance - cost_bwp

    @classmethod
    def audit_and_contain(cls, agent_id: str, tool_name: str, payload: str, estimated_cost_bwp: float = 0.0):
        now = datetime.now(timezone.utc).isoformat()
        violations = cls.evaluate_payload_sovereignty(payload)

        # 1. Check Data Sovereignty / PII Violations
        if violations:
            statute = "BW_DPA_2018"
            risk_score = 0.95
            decision = "CONTAINED_STATUTORY_HALT"
            reason = f"Statutory breach: {', '.join(violations)}"
            cls._log_audit(now, agent_id, tool_name, statute, 1, risk_score, decision, reason)
            return False, reason, decision

        # 2. Check Fiduciary Trust Account Solvency
        if estimated_cost_bwp > 0.0:
            is_solvent, sol_msg, rem_balance = cls.verify_fiduciary_solvency(agent_id, estimated_cost_bwp)
            if not is_solvent:
                statute = "BOB_FIDUCIARY_CAP"
                risk_score = 0.80
                decision = "CONTAINED_INSOLVENCY_HALT"
                reason = f"Trust rail failure: {sol_msg}"
                cls._log_audit(now, agent_id, tool_name, statute, 1, risk_score, decision, reason)
                return False, reason, decision

        # 3. Permitted Statutory Clearance
        cls._log_audit(now, agent_id, tool_name, "SOVEREIGN_CLEARANCE", 0, 0.0, "PERMITTED", "Compliant payload")
        return True, "CLEAR", "PERMITTED"

    @staticmethod
    def _log_audit(ts, agent_id, tool_name, statute, violated, risk, decision, details):
        statutory_id = hashlib.sha256(f"{ts}:{agent_id}:{tool_name}:{details}".encode('utf-8')).hexdigest()
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""
                INSERT INTO statutory_audit_ledger
                (statutory_id, timestamp, agent_id, tool_name, statute_code, violation_detected, risk_score, decision, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (statutory_id, ts, agent_id, tool_name, statute, violated, risk, decision, details))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[STATUTORY LEDGER ERROR]: {e}")
