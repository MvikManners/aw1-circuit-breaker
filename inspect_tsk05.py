import json, pymysql, os

REPO = "/home/LavetoLab/aw1-breaker"

with open(f"{REPO}/db_config.json") as f:
    cfg = json.load(f)

conn = pymysql.connect(
    host=cfg["host"], user=cfg["user"], password=cfg["password"], 
    database=cfg["database"], cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cur:
        print("=== 1. SCHEMA: accounts ===")
        cur.execute("DESCRIBE accounts;")
        for col in cur.fetchall():
            print(f"  {col['Field']:<20} {col['Type']:<20} Null: {col['Null']} Key: {col['Key']}")

        print("\n=== 2. CURRENT ACCOUNTS ROWS ===")
        cur.execute("SELECT * FROM accounts;")
        for acc in cur.fetchall():
            print(f"  {acc.get('account_id'):<18} | {acc.get('currency', 'N/A'):<5} | balance_bwp={acc.get('balance_bwp')}")

        print("\n=== 3. CHECK FOR v_accounts_normalized VIEW ===")
        cur.execute("""
            SELECT TABLE_NAME, TABLE_TYPE 
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'v_accounts_normalized';
        """, (cfg["database"],))
        v_info = cur.fetchone()
        if v_info:
            print(f"[+] Found view/table: {v_info['TABLE_NAME']} ({v_info['TABLE_TYPE']})")
            cur.execute("SHOW CREATE VIEW v_accounts_normalized;")
            v_create = cur.fetchone()
            print("  Create Definition:")
            print("  " + v_create.get("Create View", "N/A")[:200] + "...")
        else:
            print("[-] View `v_accounts_normalized` does not exist yet.")

finally:
    conn.close()

print("\n=== 4. CODEBASE REFERENCES TO balance_bwp ===")
for root, _, files in os.walk(REPO):
    if any(skip in root for skip in ["__pycache__", ".git", "docs", ".bak"]):
        continue
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                for idx, line in enumerate(fp):
                    if "balance_bwp" in line:
                        rel = os.path.relpath(path, REPO)
                        print(f"  {rel}:{idx+1} -> {line.strip()[:100]}")
