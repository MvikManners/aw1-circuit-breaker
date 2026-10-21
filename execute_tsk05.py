import json, pymysql, py_compile, shutil, sys

REPO = "/home/LavetoLab/aw1-breaker"

with open(f"{REPO}/db_config.json") as f:
    cfg = json.load(f)

conn = pymysql.connect(
    host=cfg["host"], user=cfg["user"], password=cfg["password"], 
    database=cfg["database"], cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cur:
        print("=== 1. ADD balance_nominal TO accounts ===")
        cur.execute("DESCRIBE accounts;")
        cols = {c["Field"] for c in cur.fetchall()}

        if "balance_nominal" not in cols:
            print("[+] Adding `balance_nominal` column via ALGORITHM=INSTANT...")
            try:
                cur.execute("""
                    ALTER TABLE accounts 
                    ADD COLUMN balance_nominal DECIMAL(18, 2) NULL AFTER balance_bwp,
                    ALGORITHM=INSTANT;
                """)
            except pymysql.err.OperationalError:
                print("[-] INSTANT not supported, falling back to default ALTER...")
                cur.execute("ALTER TABLE accounts ADD COLUMN balance_nominal DECIMAL(18, 2) NULL AFTER balance_bwp;")
            print("[✓] Added `balance_nominal` column.")
        else:
            print("[*] `balance_nominal` column already exists.")

        print("\n=== 2. BACKFILL balance_nominal ===")
        cur.execute("""
            UPDATE accounts 
            SET balance_nominal = balance_bwp 
            WHERE balance_nominal IS NULL;
        """)
        conn.commit()
        print(f"[✓] Backfilled {cur.rowcount} rows with nominal balances.")

        print("\n=== 3. RECREATE v_accounts_normalized VIEW ===")
        cur.execute("""
            CREATE OR REPLACE VIEW v_accounts_normalized AS 
            SELECT 
                account_id,
                account_name,
                balance_nominal,
                balance_nominal AS native_balance,
                currency,
                (CASE WHEN currency = 'BWP' THEN balance_nominal ELSE NULL END) AS domestic_bwp_balance,
                (CASE 
                    WHEN account_id IN ('STATUTORY_RESERVE_VAULT', 'FX_CLEARING_BWP', 'STATUTORY_RESERVE_USD', 'STATUTORY_RESERVE_ZAR') OR account_name LIKE '%Reserve%' THEN 'RESERVE_ESCROW'
                    WHEN account_id LIKE 'BW-AUDIT%' THEN 'TEST_STAGING'
                    ELSE 'CLIENT_LIABILITY'
                END) AS regulatory_classification,
                updated_at
            FROM accounts;
        """)
        conn.commit()
        print("[✓] Recreated `v_accounts_normalized` view with balance_nominal and zero-commingling rule.")

        print("\n=== 4. VERIFY VIEW OUTPUT ===")
        cur.execute("SELECT account_id, currency, balance_nominal, domestic_bwp_balance, regulatory_classification FROM v_accounts_normalized;")
        for row in cur.fetchall():
            print(f"  {row['account_id']:<24} | {row['currency']:<4} | Nominal: {row['balance_nominal']:>12} | Domestic BWP: {str(row['domestic_bwp_balance']):>10} | {row['regulatory_classification']}")

finally:
    conn.close()

# 5. Surgically patch release_dossier.py
print("\n=== 5. SURGICALLY PATCH release_dossier.py ===")
DOSSIER_PATH = f"{REPO}/release_dossier.py"
shutil.copyfile(DOSSIER_PATH, f"{DOSSIER_PATH}.tsk05.bak")

with open(DOSSIER_PATH, "r", encoding="utf-8") as f:
    dossier_code = f.read()

# Replace balance select
dossier_code = dossier_code.replace(
    'cur.execute("SELECT balance_bwp FROM accounts WHERE account_id = %s FOR UPDATE;", (source,))',
    'cur.execute("SELECT balance_nominal, balance_bwp FROM accounts WHERE account_id = %s FOR UPDATE;", (source,))'
)
dossier_code = dossier_code.replace(
    'v_row = cur.fetchone()\n                if not v_row or float(v_row["balance_bwp"]) < amount:',
    'v_row = cur.fetchone()\n                avail_bal = float(v_row.get("balance_nominal") or v_row.get("balance_bwp") or 0.0) if v_row else 0.0\n                if not v_row or avail_bal < amount:'
)
# Replace balance mutations
dossier_code = dossier_code.replace(
    'cur.execute("UPDATE accounts SET balance_bwp = balance_bwp - %s WHERE account_id = %s;", (amount, source))',
    'cur.execute("UPDATE accounts SET balance_bwp = balance_bwp - %s, balance_nominal = balance_nominal - %s WHERE account_id = %s;", (amount, amount, source))'
)
dossier_code = dossier_code.replace(
    'cur.execute("INSERT INTO accounts (account_id, account_name, balance_bwp, currency) VALUES (%s, %s, %s, \'BWP\');",\n                                (recipient, f"Account {recipient}", amount))',
    'cur.execute("INSERT INTO accounts (account_id, account_name, balance_bwp, balance_nominal, currency) VALUES (%s, %s, %s, %s, \'BWP\');",\n                                (recipient, f"Account {recipient}", amount, amount))'
)
dossier_code = dossier_code.replace(
    'cur.execute("UPDATE accounts SET balance_bwp = balance_bwp + %s WHERE account_id = %s;", (amount, recipient))',
    'cur.execute("UPDATE accounts SET balance_bwp = balance_bwp + %s, balance_nominal = balance_nominal + %s WHERE account_id = %s;", (amount, amount, recipient))'
)

with open(DOSSIER_PATH, "w", encoding="utf-8") as f:
    f.write(dossier_code)

py_compile.compile(DOSSIER_PATH, doraise=True)
print("[✓] release_dossier.py updated and passed compilation gate.")

# 6. Surgically patch run_checks.py
print("\n=== 6. SURGICALLY PATCH run_checks.py ===")
CHECKS_PATH = f"{REPO}/run_checks.py"
shutil.copyfile(CHECKS_PATH, f"{CHECKS_PATH}.tsk05.bak")

with open(CHECKS_PATH, "r", encoding="utf-8") as f:
    checks_code = f.read()

checks_code = checks_code.replace(
    "SELECT account_id, currency, balance_bwp AS native_balance, updated_at",
    "SELECT account_id, currency, balance_nominal AS native_balance, updated_at"
)
checks_code = checks_code.replace(
    "SELECT account_id, account_name, balance_bwp AS native_balance, currency, updated_at",
    "SELECT account_id, account_name, balance_nominal AS native_balance, currency, updated_at"
)

with open(CHECKS_PATH, "w", encoding="utf-8") as f:
    f.write(checks_code)

py_compile.compile(CHECKS_PATH, doraise=True)
print("[✓] run_checks.py updated and passed compilation gate.")
