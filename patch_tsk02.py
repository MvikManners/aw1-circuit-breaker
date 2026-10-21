import py_compile
import shutil
import sys

TARGET = "/home/LavetoLab/aw1-breaker/release_dossier.py"
BACKUP = "/home/LavetoLab/aw1-breaker/release_dossier.py.bak"

# 1. Backup original file
shutil.copyfile(TARGET, BACKUP)
print(f"[+] Backup created at {BACKUP}")

with open(TARGET, "r", encoding="utf-8") as f:
    content = f.read()

# 2. Pre-flight check: Ensure necessary modules are imported
imports_to_add = []
if "import random" not in content:
    imports_to_add.append("import random")
if "import pymysql" not in content:
    imports_to_add.append("import pymysql")

if imports_to_add:
    header_addition = "\n".join(imports_to_add) + "\n"
    content = header_addition + content
    print(f"[+] Injected required imports: {imports_to_add}")

# 3. Define exact search anchor block
old_block = """    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT balance_bwp FROM accounts WHERE account_id = %s FOR UPDATE;", (source,))
        v_row = cur.fetchone()
        if not v_row or float(v_row["balance_bwp"]) < amount:
            conn.rollback()
            conn.close()
            avail = float(v_row["balance_bwp"]) if v_row else 0.0
            print(f"FAILED: Vault balance ({avail:,.2f} BWP) insufficient for override.")
            sys.exit(1)

        cur.execute("UPDATE accounts SET balance_bwp = balance_bwp - %s WHERE account_id = %s;", (amount, source))
        cur.execute("SELECT balance_bwp FROM accounts WHERE account_id = %s FOR UPDATE;", (recipient,))
        if cur.fetchone() is None:
            cur.execute("INSERT INTO accounts (account_id, account_name, balance_bwp, currency) VALUES (%s, %s, %s, 'BWP');",
                        (recipient, f"Account {recipient}", amount))
        else:
            cur.execute("UPDATE accounts SET balance_bwp = balance_bwp + %s WHERE account_id = %s;", (amount, recipient))

        cur.execute(\"\"\"
            INSERT INTO ledger_entries (source_account, destination_account, amount_bwp, execution_token, dossier_hash)
            VALUES (%s, %s, %s, %s, %s);
        \"\"\", (source, recipient, amount, override_token, dossier_hash))
        entry_id = cur.lastrowid
        conn.commit()
    conn.close()"""

# 4. Define robust CAS retry replacement block
new_block = """    # CAS Retry Loop with Exponential Backoff & Hash Chaining
    max_retries = 5
    base_backoff_ms = 8.0
    entry_id = None
    committed_parent_hash = None

    for attempt in range(max_retries):
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # 1. Balance verification under row lock
                cur.execute("SELECT balance_bwp FROM accounts WHERE account_id = %s FOR UPDATE;", (source,))
                v_row = cur.fetchone()
                if not v_row or float(v_row["balance_bwp"]) < amount:
                    conn.rollback()
                    avail = float(v_row["balance_bwp"]) if v_row else 0.0
                    print(f"FAILED: Vault balance ({avail:,.2f} BWP) insufficient for override.")
                    sys.exit(1)

                # 2. Tip resolution for deterministic parent_hash lineage
                cur.execute("SELECT entry_id, dossier_hash FROM ledger_entries ORDER BY entry_id DESC LIMIT 1 FOR UPDATE;")
                tip = cur.fetchone()
                if tip and tip.get("dossier_hash"):
                    parent_hash = tip["dossier_hash"]
                else:
                    parent_hash = "0" * 64

                # 3. Account balance mutation
                cur.execute("UPDATE accounts SET balance_bwp = balance_bwp - %s WHERE account_id = %s;", (amount, source))
                cur.execute("SELECT balance_bwp FROM accounts WHERE account_id = %s FOR UPDATE;", (recipient,))
                if cur.fetchone() is None:
                    cur.execute("INSERT INTO accounts (account_id, account_name, balance_bwp, currency) VALUES (%s, %s, %s, 'BWP');",
                                (recipient, f"Account {recipient}", amount))
                else:
                    cur.execute("UPDATE accounts SET balance_bwp = balance_bwp + %s WHERE account_id = %s;", (amount, recipient))

                # 4. Structured node telemetry payload
                telemetry_data = {
                    "officer_id": officer_id,
                    "statutory_scope": "BOB_EPS_SEC14",
                    "kms_mode": "AES-256-GCM_ENCLAVE",
                    "lineage": "SHA256_CHAIN_V1",
                    "retry_attempt": attempt
                }

                # 5. Insert chained ledger entry
                cur.execute(\"\"\"
                    INSERT INTO ledger_entries (
                        source_account, destination_account, amount_bwp, 
                        execution_token, dossier_hash, parent_hash, node_telemetry
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s);
                \"\"\", (source, recipient, amount, override_token, dossier_hash, parent_hash, json.dumps(telemetry_data)))
                entry_id = cur.lastrowid
                conn.commit()
                committed_parent_hash = parent_hash
                break

        except pymysql.err.OperationalError as e:
            conn.rollback()
            if e.args[0] in (1205, 1213) and attempt < max_retries - 1:
                sleep_sec = (base_backoff_ms * (2 ** attempt) + random.uniform(1.0, 4.0)) / 1000.0
                time.sleep(sleep_sec)
                continue
            raise RuntimeError(f"FATAL: Database write-lock contention exhausted ({e})")
        except pymysql.err.IntegrityError as e:
            conn.rollback()
            if attempt < max_retries - 1:
                sleep_sec = (base_backoff_ms * (2 ** attempt) + random.uniform(1.0, 4.0)) / 1000.0
                time.sleep(sleep_sec)
                continue
            raise RuntimeError(f"FATAL: Ledger integrity collision on parent_hash ({e})")
        finally:
            conn.close()

    if entry_id is None:
        print("FAILED: Audit ledger transaction could not be committed after maximum retries.")
        sys.exit(1)"""

# 5. Anchor check and surgical substitution
if old_block not in content:
    print("[!] ERROR: Target block anchor not matched exactly. Aborting without changes.")
    sys.exit(1)

content = content.replace(old_block, new_block, 1)

# Also bind parent_hash into the dossier JSON object
dossier_anchor = '    dossier["ledger_entry_id"] = entry_id'
dossier_replacement = '    dossier["ledger_entry_id"] = entry_id\n    dossier["parent_hash"] = committed_parent_hash'
if dossier_anchor in content:
    content = content.replace(dossier_anchor, dossier_replacement, 1)

with open(TARGET, "w", encoding="utf-8") as f:
    f.write(content)

print("[+] Surgical patch written to release_dossier.py.")

# 6. Mandatory compilation gate
print("=== MANDATORY COMPILATION GATE ===")
try:
    py_compile.compile(TARGET, doraise=True)
    print("[✓] Compilation successful: release_dossier.py has valid Python syntax.")
except py_compile.PyCompileError as e:
    print(f"[!] Compilation FAILED: {e}")
    shutil.copyfile(BACKUP, TARGET)
    print("[-] Reverted to backup.")
    sys.exit(1)
