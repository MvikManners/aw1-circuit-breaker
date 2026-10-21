import os, json, pymysql

REPO = "/home/LavetoLab/aw1-breaker"

print("=== 1. SEARCH FOR LEDGER INSERTIONS IN CODEBASE ===")
for root, _, files in os.walk(REPO):
    if any(skip in root for skip in ["__pycache__", ".git", "docs"]):
        continue
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                for idx, line in enumerate(fp):
                    if "ledger_entries" in line and any(w in line for w in ["INSERT", "insert", "execute", "cursor"]):
                        rel = os.path.relpath(path, REPO)
                        print(f"  {rel}:{idx+1} -> {line.strip()[:100]}")

print("\n=== 2. CURRENT STATUS OF ENTRIES #31–#43 parent_hash ===")
with open("/home/LavetoLab/aw1-breaker/db_config.json") as f:
    cfg = json.load(f)

conn = pymysql.connect(
    host=cfg["host"], user=cfg["user"], password=cfg["password"], 
    database=cfg["database"], cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute("""
        SELECT entry_id, dossier_hash, parent_hash, timestamp 
        FROM ledger_entries 
        WHERE entry_id >= 31 
        ORDER BY entry_id ASC;
    """)
    rows = cur.fetchall()
    for r in rows:
        ph = r["parent_hash"] if r["parent_hash"] else "NULL"
        print(f"  Entry #{r['entry_id']}: dossier_hash={r['dossier_hash'][:16]}... | parent_hash={ph}")
conn.close()
