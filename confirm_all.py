import json
import os
import sys
import py_compile
import pymysql
import subprocess
from decimal import Decimal

REPO = "/home/LavetoLab/aw1-breaker"
PASS_COUNT = 0
FAIL_COUNT = 0

def check(name, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  [\033[92mPASS\033[0m] {name} {detail}")
    else:
        FAIL_COUNT += 1
        print(f"  [\033[91mFAIL\033[0m] {name} {detail}")

print("======================================================================")
print("       AW-1 MASTER SYSTEM AUDIT & REMEDIATION VERIFICATION           ")
print("======================================================================")

# --- 1. CODE COMPILATION GATE ---
print("\n[1/7] Python Source Compilation Gate")
for py_file in ["release_dossier.py", "aw1_hcs_worker.py", "run_checks.py"]:
    full_path = os.path.join(REPO, py_file)
    if not os.path.exists(full_path):
        check(f"Existence of {py_file}", False, "(File missing)")
        continue
    try:
        py_compile.compile(full_path, doraise=True)
        check(f"Syntax validation for {py_file}", True)
    except Exception as e:
        check(f"Syntax validation for {py_file}", False, f"({e})")

# --- 2. HCS SANDBOX & CONFIG SANITIZATION (TSK-04) ---
print("\n[2/7] HCS Sandbox Configuration & Monotonicity (TSK-04)")
cfg_path = os.path.join(REPO, "hcs_config.json")
if os.path.exists(cfg_path):
    with open(cfg_path, "r", encoding="utf-8") as f:
        hcs_cfg = json.load(f)
    
    check("Sandbox mode configured", hcs_cfg.get("mode") == "SIMULATED_SANDBOX")
    check("Dry run enabled", hcs_cfg.get("dry_run") is True)
    check("Topic placeholder removed", "YOUR_TOPIC_ID" not in str(hcs_cfg.get("topic_id")))
    check("Operator placeholder removed", "YOUR_ACCOUNT_ID" not in str(hcs_cfg.get("operator_account_id")))
    
    try:
        from aw1_hcs_worker import HederaHCSClient
        with open(os.path.join(REPO, "db_config.json")) as f:
            db_cfg = json.load(f)
        client = HederaHCSClient(hcs_cfg, db_cfg=db_cfg)
        r1 = client.submit_attestation({"dossier_hash": "audit_probe_hash_1", "audit_id": 10001})
        r2 = client.submit_attestation({"dossier_hash": "audit_probe_hash_2", "audit_id": 10002})
        
        check("Monotonic sequence increment", r2["sequence_number"] == r1["sequence_number"] + 1,
              f"(Seq: {r1['sequence_number']} -> {r2['sequence_number']})")
        check("Sequence baseline threshold", r1["sequence_number"] >= 512111,
              f"(Min expected 512111, got {r1['sequence_number']})")
        check("Double-prefix eliminated", not r1["tx_id"].startswith("0.0.0.0."), f"({r1['tx_id'][:32]})")
        check("Attestation mode tag", r1.get("mode") == "SIMULATED_SANDBOX")
    except Exception as e:
        check("HCS client dry-run execution", False, f"({e})")
else:
    check("hcs_config.json exists", False)

# --- DATABASE CONNECTION & REPOSITORIES ---
with open(os.path.join(REPO, "db_config.json")) as f:
    db_cfg = json.load(f)

conn = pymysql.connect(
    host=db_cfg["host"], user=db_cfg["user"], password=db_cfg["password"],
    database=db_cfg["database"], cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cur:
        # --- 3. DATABASE SCHEMA HARDENING (TSK-01 & TSK-05) ---
        print("\n[3/7] Database Schema Hardening (TSK-01, TSK-05)")
        cur.execute("DESCRIBE ledger_entries;")
        ledger_cols = {c["Field"] for c in cur.fetchall()}
        check("Column parent_hash in ledger_entries", "parent_hash" in ledger_cols)
        check("Column node_telemetry in ledger_entries", "node_telemetry" in ledger_cols)
        
        cur.execute("DESCRIBE accounts;")
        acc_cols = {c["Field"] for c in cur.fetchall()}
        check("Column balance_nominal in accounts", "balance_nominal" in acc_cols)
        
        cur.execute("SELECT COUNT(*) AS cnt FROM accounts WHERE balance_nominal IS NULL;")
        null_bal_cnt = cur.fetchone()["cnt"]
        check("All nominal balances backfilled", null_bal_cnt == 0, f"({null_bal_cnt} NULL accounts)")

        # --- 4. CRYPTOGRAPHIC CHAIN LINEAGE INTEGRITY (TSK-02 & TSK-03) ---
        print("\n[4/7] Cryptographic Chain Lineage Integrity (TSK-02, TSK-03)")
        cur.execute("""
            SELECT entry_id, dossier_hash, parent_hash 
            FROM ledger_entries 
            WHERE entry_id BETWEEN 31 AND 43 
            ORDER BY entry_id ASC;
        """)
        chain_rows = cur.fetchall()
        check("Chain rows count (#31 to #43)", len(chain_rows) == 13, f"(Found {len(chain_rows)} entries)")
        
        if chain_rows:
            genesis = chain_rows[0]
            check("Genesis Root (#31) zero-parent anchor",
                  genesis["parent_hash"] == "0000000000000000000000000000000000000000000000000000000000000000",
                  f"({genesis['parent_hash'][:16]}...)")
            
            chain_broken = False
            broken_details = ""
            for i in range(1, len(chain_rows)):
                prev_dossier = chain_rows[i-1]["dossier_hash"].lower().replace("0x", "")
                curr_parent = (chain_rows[i]["parent_hash"] or "").lower().replace("0x", "")
                if prev_dossier != curr_parent:
                    chain_broken = True
                    broken_details = f"(Mismatch at entry #{chain_rows[i]['entry_id']}: expected {prev_dossier[:10]}, got {curr_parent[:10]})"
                    break
            check("Unbroken SHA-256 parent lineage (#31-#43)", not chain_broken, broken_details)

        # --- 5. MULTI-CURRENCY SOLVENCY & COMMINGLING PROHIBITION (TSK-05) ---
        print("\n[5/7] Multi-Currency Silo Solvency & Commingling Segregation (TSK-05)")
        cur.execute("SELECT * FROM v_accounts_normalized;")
        v_rows = cur.fetchall()
        
        foreign_commingled = [r for r in v_rows if r["currency"] != "BWP" and r["domestic_bwp_balance"] is not None]
        check("Strict Zero-Commingling: Foreign assets exclude domestic BWP",
              len(foreign_commingled) == 0,
              f"({len(foreign_commingled)} violating accounts)")
        
        bwp_escrow = sum(r["balance_nominal"] for r in v_rows if r["currency"] == "BWP" and r["regulatory_classification"] == "RESERVE_ESCROW")
        bwp_liab = sum(r["balance_nominal"] for r in v_rows if r["currency"] == "BWP" and r["regulatory_classification"] == "CLIENT_LIABILITY")
        bwp_ratio = (bwp_escrow / bwp_liab * 100) if bwp_liab > 0 else Decimal(0)
        
        usd_escrow = sum(r["balance_nominal"] for r in v_rows if r["currency"] == "USD" and r["regulatory_classification"] == "RESERVE_ESCROW")
        usd_liab = sum(r["balance_nominal"] for r in v_rows if r["currency"] == "USD" and r["regulatory_classification"] == "CLIENT_LIABILITY")
        usd_ratio = (usd_escrow / usd_liab * 100) if usd_liab > 0 else Decimal(0)
        
        zar_escrow = sum(r["balance_nominal"] for r in v_rows if r["currency"] == "ZAR" and r["regulatory_classification"] == "RESERVE_ESCROW")
        zar_liab = sum(r["balance_nominal"] for r in v_rows if r["currency"] == "ZAR" and r["regulatory_classification"] == "CLIENT_LIABILITY")
        zar_ratio = (zar_escrow / zar_liab * 100) if zar_liab > 0 else Decimal(0)

        check("BWP Silo Solvency (>= 100%)", bwp_ratio >= 100, f"({bwp_ratio:.2f}% | Escrow: P{bwp_escrow:,.2f} vs Liab: P{bwp_liab:,.2f})")
        check("USD Silo Solvency (376.19% Target)", round(usd_ratio, 2) == Decimal("376.19"), f"({usd_ratio:.2f}% | Escrow: ${usd_escrow:,.2f} vs Liab: ${usd_liab:,.2f})")
        check("ZAR Silo Solvency (> 100%)", zar_ratio > 100, f"({zar_ratio:,.2f}% | Escrow: R{zar_escrow:,.2f} vs Liab: R{zar_liab:,.2f})")

        # --- 6. QUARANTINE PARTITION ISOLATION ---
        print("\n[6/7] Quarantine Partition & ISO 20022 Isolation")
        cur.execute("DESCRIBE ledger_entries_quarantine;")
        q_fields = [c["Field"] for c in cur.fetchall()]
        
        amt_col = next((c for c in ["amount_bwp", "amount", "balance_bwp"] if c in q_fields), None)
        
        if amt_col:
            cur.execute(f"SELECT COUNT(*) AS cnt, SUM({amt_col}) AS total FROM ledger_entries_quarantine;")
            q_data = cur.fetchone()
            total_val = float(q_data['total']) if q_data['total'] is not None else 0.0
            check("Quarantine partition isolation (11 rows, P130,000.00)", 
                  q_data["cnt"] == 11 and abs(total_val - 130000.0) < 0.01, 
                  f"({q_data['cnt']} rows, P{total_val:,.2f})")
        else:
            cur.execute("SELECT COUNT(*) AS cnt FROM ledger_entries_quarantine;")
            q_data = cur.fetchone()
            check("Quarantine partition isolation (11 rows)", q_data["cnt"] == 11, f"({q_data['cnt']} rows)")
        
        cur.execute("SELECT COUNT(*) AS cnt FROM iso20022_audit_log WHERE entry_id BETWEEN 16 AND 26;")
        iso_leakage = cur.fetchone()["cnt"]
        check("Zero ISO 20022 message leakage from quarantine", iso_leakage == 0, f"({iso_leakage} emitted messages)")

finally:
    conn.close()

# --- 7. AUDIT DOSSIER ARTIFACT VERIFICATION ---
print("\n[7/7] Audit Deliverables & Documentation")
pdf_path = os.path.join(REPO, "AW1_Ledger_Technical_Audit_Dossier_v2.0.1.pdf")
if os.path.exists(pdf_path):
    size_kb = os.path.getsize(pdf_path) / 1024
    check("Technical Audit Dossier PDF exists", True, f"({pdf_path} - {size_kb:.1f} KB)")
else:
    check("Technical Audit Dossier PDF exists", False, "(Run generate_audit_pdf.py)")

print("\n======================================================================")
print(f"VERIFICATION SUMMARY: \033[92m{PASS_COUNT} PASSED\033[0m, \033[91m{FAIL_COUNT} FAILED\033[0m")
if FAIL_COUNT == 0:
    print("\033[92mALL 25 STATUTORY & ARCHITECTURAL CHECKS VERIFIED CLEAN (100%).\033[0m")
else:
    print("ATTENTION REQUIRED: One or more audit checks failed.")
print("======================================================================")
