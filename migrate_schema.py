import json, pymysql

with open("/home/LavetoLab/aw1-breaker/db_config.json") as f:
    cfg = json.load(f)

conn = pymysql.connect(
    host=cfg["host"], user=cfg["user"], password=cfg["password"], 
    database=cfg["database"], cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cur:
        print("=== 1. CHECK CURRENT COLUMNS ===")
        cur.execute("DESCRIBE ledger_entries;")
        existing_cols = {c["Field"] for c in cur.fetchall()}
        print(f"Existing columns ({len(existing_cols)}): {sorted(list(existing_cols))}")

        # 2. Add parent_hash if missing
        if "parent_hash" not in existing_cols:
            print("[+] Adding `parent_hash` column via ALGORITHM=INSTANT...")
            try:
                cur.execute("""
                    ALTER TABLE ledger_entries 
                    ADD COLUMN parent_hash VARCHAR(64) NULL AFTER dossier_hash,
                    ALGORITHM=INSTANT;
                """)
            except pymysql.err.OperationalError:
                print("[-] INSTANT not supported for parent_hash, falling back to default...")
                cur.execute("ALTER TABLE ledger_entries ADD COLUMN parent_hash VARCHAR(64) NULL AFTER dossier_hash;")
            print("[✓] `parent_hash` added successfully.")
        else:
            print("[*] `parent_hash` already exists.")

        # 3. Add node_telemetry if missing
        if "node_telemetry" not in existing_cols:
            print("[+] Adding `node_telemetry` JSON column via ALGORITHM=INSTANT...")
            try:
                cur.execute("""
                    ALTER TABLE ledger_entries 
                    ADD COLUMN node_telemetry JSON NULL,
                    ALGORITHM=INSTANT;
                """)
            except pymysql.err.OperationalError:
                print("[-] INSTANT not supported for node_telemetry, falling back to default...")
                cur.execute("ALTER TABLE ledger_entries ADD COLUMN node_telemetry JSON NULL;")
            print("[✓] `node_telemetry` added successfully.")
        else:
            print("[*] `node_telemetry` already exists.")

        conn.commit()

        print("\n=== 2. VERIFY NEW SCHEMA ===")
        cur.execute("DESCRIBE ledger_entries;")
        for c in cur.fetchall():
            if c["Field"] in ("entry_id", "dossier_hash", "parent_hash", "node_telemetry"):
                print(f"  {c['Field']:<18} {c['Type']:<20} Nullable: {c['Null']}")

finally:
    conn.close()

print("\n[+] TSK-01 Migration script executed cleanly.")
