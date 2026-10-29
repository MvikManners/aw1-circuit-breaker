import random
import pymysql
#!/usr/bin/env python3
import sys, os, json, glob, time, secrets, pymysql
from crypto_engine import get_kms_provider, KEY_STORE

DOSSIER_DIR = "/home/LavetoLab/aw1-breaker/dossiers"
DB_CONFIG_PATH = "/home/LavetoLab/aw1-breaker/db_config.json"
provider = get_kms_provider()

def get_db_connection():
    with open(DB_CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return pymysql.connect(
        host=cfg["host"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        port=cfg.get("port", 3306),
        charset="utf8mb4",
        autocommit=False,
        cursorclass=pymysql.cursors.DictCursor
    )

def release_dossier(hash_prefix: str, officer_id: str, signature_hex: str):
    if not os.path.exists(KEY_STORE):
        print("ERROR: Compliance key registry not initialized.")
        sys.exit(1)

    with open(KEY_STORE, "r", encoding="utf-8") as kf:
        registry = json.load(kf)

    officer_profile = registry.get(officer_id)
    if not officer_profile or not officer_profile.get("active"):
        print(f"SECURITY_ABORT: Officer ID '{officer_id}' is not an active, authorized signatory.")
        sys.exit(1)

    matches = glob.glob(os.path.join(DOSSIER_DIR, f"*{hash_prefix}*.json"))
    if not matches:
        print(f"ERROR: No dossier found matching prefix: {hash_prefix}")
        sys.exit(1)

    dossier_path = matches[0]
    with open(dossier_path, "r", encoding="utf-8") as fp:
        dossier = json.load(fp)

    if dossier.get("status") == "RELEASED_BY_OVERRIDE":
        print(f"ABORT: Dossier {hash_prefix} has already been released on {dossier.get('override_timestamp')}.")
        sys.exit(1)

    dossier_hash = dossier.get("dossier_hash", "")

    # Enterprise KMS Cryptographic Signature Verification Gate
    if not provider.verify_signature(officer_id, dossier_hash, signature_hex):
        print(f"SECURITY_ALERT: Cryptographic signature verification failed for {officer_id}.")
        print("ABORTING: Tampered signature or untrusted key.")
        sys.exit(1)

    print(f"[KMS_CRYPTO_VERIFIED] Hardware Enclave confirmed signature for {officer_id}.")

    amount = float(dossier.get("amount", 0.0))
    payload = dossier.get("payload", {})
    recipient = payload.get("recipient", "UNKNOWN")
    source = "STATUTORY_RESERVE_VAULT"

    # Discretionary Spending Limit Gate
    limit_bwp = float(officer_profile.get("spending_limit_bwp", 0.0))
    if amount > limit_bwp:
        print(f"SECURITY_ALERT: Quarantined amount ({amount:,.2f} BWP) exceeds discretionary limit ({limit_bwp:,.2f} BWP) for {officer_id}.")
        print("ABORTING: Escalation required. Signatory authorization insufficient.")
        sys.exit(1)

    print(f"\n{'!'*20} ED25519 KMS OVERRIDE {'!'*20}")
    print(f"Dossier:      {dossier_hash}")
    print(f"Action:       Disburse {amount:,.2f} BWP -> {recipient}")
    print(f"Officer:      {officer_id} ({officer_profile.get('name')})")

    override_token = f"AW1-OVERRIDE-KMS-{secrets.token_hex(8)}"

    # CAS Retry Loop with Exponential Backoff & Hash Chaining
    max_retries = 5
    base_backoff_ms = 8.0
    entry_id = None
    committed_parent_hash = None

    for attempt in range(max_retries):
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # 1. Balance verification under row lock
                cur.execute("SELECT balance_nominal, balance_bwp FROM accounts WHERE account_id = %s FOR UPDATE;", (source,))
                v_row = cur.fetchone()
                avail_bal = float(v_row.get("balance_nominal") or v_row.get("balance_bwp") or 0.0) if v_row else 0.0
                if not v_row or avail_bal < amount:
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
                cur.execute("UPDATE accounts SET balance_bwp = balance_bwp - %s, balance_nominal = balance_nominal - %s WHERE account_id = %s;", (amount, amount, source))
                cur.execute("SELECT balance_bwp FROM accounts WHERE account_id = %s FOR UPDATE;", (recipient,))
                if cur.fetchone() is None:
                    cur.execute("INSERT INTO accounts (account_id, account_name, balance_bwp, balance_nominal, currency) VALUES (%s, %s, %s, %s, 'BWP');",
                                (recipient, f"Account {recipient}", amount, amount))
                else:
                    cur.execute("UPDATE accounts SET balance_bwp = balance_bwp + %s, balance_nominal = balance_nominal + %s WHERE account_id = %s;", (amount, amount, recipient))

                # 4. Structured node telemetry payload
                telemetry_data = {
                    "officer_id": officer_id,
                    "statutory_scope": "BOB_EPS_SEC14",
                    "kms_mode": "AES-256-GCM_ENCLAVE",
                    "lineage": "SHA256_CHAIN_V1",
                    "retry_attempt": attempt
                }

                # 5. Insert chained ledger entry
                cur.execute("""
                    INSERT INTO ledger_entries (
                        source_account, destination_account, amount_bwp, 
                        execution_token, dossier_hash, parent_hash, node_telemetry
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s);
                """, (source, recipient, amount, override_token, dossier_hash, parent_hash, json.dumps(telemetry_data)))
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
        sys.exit(1)

    dossier["status"] = "RELEASED_BY_OVERRIDE"
    dossier["override_token"] = override_token
    dossier["released_by"] = officer_id
    dossier["ed25519_signature"] = signature_hex
    dossier["override_timestamp"] = time.time()
    dossier["ledger_entry_id"] = entry_id
    dossier["parent_hash"] = committed_parent_hash
    dossier["kms_mode"] = "AES-256-GCM_ENCLAVE"

    with open(dossier_path, "w", encoding="utf-8") as fp:
        json.dump(dossier, fp, indent=2)

    print(f"SUCCESS: Ledger Entry #{entry_id:03d} committed under {override_token}.")
    print(f"Dossier {os.path.basename(dossier_path)} sealed with KMS audit proof.")

if __name__ == "__main__":
    if len(sys.argv) >= 4:
        release_dossier(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print("Usage: python3 release_dossier.py <hash_prefix> <officer_id> <signature_hex>")
