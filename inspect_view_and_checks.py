import json, pymysql

with open("/home/LavetoLab/aw1-breaker/db_config.json") as f:
    cfg = json.load(f)

conn = pymysql.connect(
    host=cfg["host"], user=cfg["user"], password=cfg["password"], 
    database=cfg["database"], cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cur:
        print("=== 1. FULL VIEW DEFINITION: v_accounts_normalized ===")
        cur.execute("SHOW CREATE VIEW v_accounts_normalized;")
        row = cur.fetchone()
        print(row.get("Create View", "Not found"))

        print("\n=== 2. CURRENT DATA FROM v_accounts_normalized ===")
        cur.execute("SELECT * FROM v_accounts_normalized;")
        for r in cur.fetchall():
            print(f"  {r}")
finally:
    conn.close()

print("\n=== 3. INSPECT run_checks.py (Lines 25 to 65) ===")
with open("/home/LavetoLab/aw1-breaker/run_checks.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i in range(24, min(len(lines), 65)):
    print(f"{i+1:3d}: {lines[i]}", end="")
