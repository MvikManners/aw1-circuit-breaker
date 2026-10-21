import json, os, urllib.request, pymysql

with open("/home/LavetoLab/aw1-breaker/db_config.json") as f:
    cfg = json.load(f)

conn = pymysql.connect(
    host=cfg["host"], user=cfg["user"], password=cfg["password"], 
    database=cfg["database"], cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    print("=== 1. QUARANTINED ROWS (ledger_entries_quarantine) ===")
    cur.execute("""
        SELECT 
            COUNT(*) AS total_quarantined_rows, 
            SUM(amount_bwp) AS total_quarantined_amount, 
            MIN(original_entry_id) AS min_id, 
            MAX(original_entry_id) AS max_id 
        FROM ledger_entries_quarantine;
    """)
    print(json.dumps(cur.fetchone(), indent=2, default=str))

    print("\n=== 2. ISO 20022 MESSAGE EMISSION CHECK (#16-#26) ===")
    cur.execute("""
        SELECT id, entry_id, message_id, status 
        FROM iso20022_audit_log 
        WHERE entry_id BETWEEN 16 AND 26;
    """)
    iso_rows = cur.fetchall()
    print(f"Emitted messages found for entries 16-26: {len(iso_rows)}")
    for r in iso_rows:
        print(" ", r)

    print("\n=== 3. USD ACCOUNTS UPDATED_AT VS QUARANTINE ===")
    cur.execute("""
        SELECT account_id, currency, balance_nominal AS native_balance, updated_at 
        FROM accounts 
        WHERE account_id IN ('STATUTORY_RESERVE_USD', 'US-PARTNER-NODE-09');
    """)
    for acc in cur.fetchall():
        print(f"  {acc['account_id']}: balance={acc['native_balance']} {acc['currency']} (updated_at: {acc['updated_at']})")

    print("\n=== 4. COMPLETE USD SILO POPULATION ===")
    cur.execute("""
        SELECT account_id, account_name, balance_nominal AS native_balance, currency, updated_at 
        FROM accounts 
        WHERE currency = 'USD';
    """)
    usd_silo = cur.fetchall()
    print(f"Total USD accounts: {len(usd_silo)}")
    for acc in usd_silo:
        print(f"  {acc['account_id']} ({acc['account_name']}): {acc['native_balance']} USD (updated_at: {acc['updated_at']})")

conn.close()

print("\n=== 5. RECENT uWSGI SERVER LOG (Last 20 lines) ===")
server_log = "/var/log/lavetolab.pythonanywhere.com.server.log"
if os.path.exists(server_log):
    with open(server_log, "r", encoding="utf-8") as f:
        print("".join(f.readlines()[-20:]))

print("\n=== 6. PRE-WARMING GATEWAY ===")
try:
    req = urllib.request.Request("https://lavetolab.pythonanywhere.com/", headers={"User-Agent": "GatewayWarmup/1.0"})
    urllib.request.urlopen(req, timeout=10)
    print("[+] Gateway is active and listening.")
except urllib.error.HTTPError as e:
    print(f"[+] Gateway responded with HTTP {e.code} (Worker active).")
except Exception as e:
    print(f"[!] Gateway ping note: {e}")
