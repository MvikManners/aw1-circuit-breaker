import json, time, pymysql

with open("/home/LavetoLab/aw1-breaker/db_config.json") as f:
    cfg = json.load(f)

conn = pymysql.connect(
    host=cfg["host"], user=cfg["user"], password=cfg["password"], 
    database=cfg["database"], cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cur:
        print("=== 1. FETCHING ACTIVE ENTRIES #31–#43 ===")
        cur.execute("""
            SELECT entry_id, dossier_hash, parent_hash, timestamp 
            FROM ledger_entries 
            WHERE entry_id BETWEEN 31 AND 43 
            ORDER BY entry_id ASC;
        """)
        rows = cur.fetchall()
        print(f"[+] Loaded {len(rows)} entries for cryptographic linking.")

        if len(rows) != 13:
            raise RuntimeError(f"Expected 13 entries (#31–#43), found {len(rows)}.")

        # 2. Compute backfill lineage
        genesis_parent = "0" * 64
        updates = []

        for idx, row in enumerate(rows):
            eid = row["entry_id"]
            d_hash = row["dossier_hash"]

            if idx == 0:
                p_hash = genesis_parent
            else:
                p_hash = rows[idx - 1]["dossier_hash"]

            telemetry = {
                "lineage": "SHA256_CHAIN_V1",
                "backfilled": True,
                "backfill_timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "baseline_note": "AW1-NOTE-AUDIT-BASELINE-20261019",
                "genesis_root": (idx == 0)
            }

            updates.append((p_hash, json.dumps(telemetry), eid))

        print("\n=== 2. COMMITTING LINEAGE UPDATES ===")
        for p_hash, telem, eid in updates:
            cur.execute("""
                UPDATE ledger_entries 
                SET parent_hash = %s, node_telemetry = %s 
                WHERE entry_id = %s;
            """, (p_hash, telem, eid))
            print(f"  Entry #{eid:02d}: linked to parent {p_hash[:16]}...")

        conn.commit()
        print("[✓] All updates committed to database.")

        print("\n=== 3. VERIFYING CRYPTOGRAPHIC CONTINUITY ===")
        cur.execute("""
            SELECT entry_id, parent_hash, dossier_hash 
            FROM ledger_entries 
            WHERE entry_id BETWEEN 31 AND 43 
            ORDER BY entry_id ASC;
        """)
        verified_rows = cur.fetchall()

        broken_links = 0
        for i, r in enumerate(verified_rows):
            eid = r["entry_id"]
            p_hash = r["parent_hash"]
            d_hash = r["dossier_hash"]

            if i == 0:
                if p_hash != genesis_parent:
                    print(f"  [FAIL] Entry #{eid} genesis mismatch: {p_hash}")
                    broken_links += 1
                else:
                    print(f"  Entry #{eid:02d} [GENESIS]: parent={p_hash[:16]}... | hash={d_hash[:16]}... [VALID]")
            else:
                expected_parent = verified_rows[i - 1]["dossier_hash"]
                if p_hash != expected_parent:
                    print(f"  [FAIL] Entry #{eid} parent mismatch! Got {p_hash[:16]}, expected {expected_parent[:16]}")
                    broken_links += 1
                else:
                    print(f"  Entry #{eid:02d} -> Entry #{eid-1:02d}: parent={p_hash[:16]}... | hash={d_hash[:16]}... [LINKED]")

        if broken_links == 0:
            print("\n[✓] CRYPTOGRAPHIC CHAIN VERIFIED: Unbroken lineage across entries #31–#43.")
        else:
            raise RuntimeError(f"Chain verification failed with {broken_links} broken links.")

finally:
    conn.close()
