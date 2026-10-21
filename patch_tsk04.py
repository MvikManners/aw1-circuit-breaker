import py_compile
import shutil
import sys
import json

CONFIG_FILE = "/home/LavetoLab/aw1-breaker/hcs_config.json"
CONFIG_BAK = "/home/LavetoLab/aw1-breaker/hcs_config.json.bak"
WORKER_FILE = "/home/LavetoLab/aw1-breaker/aw1_hcs_worker.py"
WORKER_BAK = "/home/LavetoLab/aw1-breaker/aw1_hcs_worker.py.bak"

# 1. Create backups
shutil.copyfile(CONFIG_FILE, CONFIG_BAK)
shutil.copyfile(WORKER_FILE, WORKER_BAK)
print(f"[+] Backups created: {CONFIG_BAK}, {WORKER_BAK}")

# 2. Sanitize hcs_config.json
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    cfg = json.load(f)

cfg["mode"] = "SIMULATED_SANDBOX"
cfg["operator_account_id"] = "0.0.SIMULATED_OPERATOR"
cfg["operator_private_key"] = "SIMULATED_KEY_SANDBOX_MODE_ONLY"
cfg["topic_id"] = "0.0.SIMULATED_SANDBOX_TOPIC"
cfg["dry_run"] = True

with open(CONFIG_FILE, "w", encoding="utf-8") as f:
    json.dump(cfg, f, indent=2)
print("[+] Sanitized hcs_config.json with explicit SIMULATED_SANDBOX mode and clean identifiers.")

# 3. Surgically patch aw1_hcs_worker.py
with open(WORKER_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Anchor 1: HederaHCSClient.__init__
old_init = """class HederaHCSClient:
    \"\"\"Manages HCS topic submissions via native SDK or REST fallback.\"\"\"
    def __init__(self, config: dict):
        self.config = config
        self.dry_run = config.get("dry_run", False)
        self.topic_id = config.get("topic_id")
        self.network = config.get("network", "testnet")
        self.sdk_available = False"""

new_init = """class HederaHCSClient:
    \"\"\"Manages HCS topic submissions via native SDK or REST fallback.\"\"\"
    def __init__(self, config: dict, db_cfg: dict = None):
        self.config = config
        self.dry_run = config.get("dry_run", False)
        self.topic_id = config.get("topic_id", "0.0.SIMULATED_SANDBOX_TOPIC")
        self.network = config.get("network", "testnet")
        self.mode = config.get("mode", "SIMULATED_SANDBOX" if self.dry_run else "LIVE")
        self.sdk_available = False
        self._seq_counter = 512111

        if self.dry_run and db_cfg:
            try:
                conn = get_db_connection(db_cfg)
                with conn.cursor() as cur:
                    cur.execute("SELECT COALESCE(MAX(hcs_sequence_number), 512110) AS max_seq FROM aw1_hcs_anchors;")
                    row = cur.fetchone()
                    if row and row.get("max_seq"):
                        self._seq_counter = int(row["max_seq"]) + 1
                conn.close()
            except Exception as e:
                logger.warning(f"Could not initialize monotonic sequence from DB: {e}")"""

if old_init not in content:
    print("[!] ERROR: Anchor old_init not found in aw1_hcs_worker.py. Aborting.")
    sys.exit(1)

content = content.replace(old_init, new_init, 1)

# Anchor 2: submit_attestation dry_run branch
old_submit_dry = """        if self.dry_run:
            # Deterministic simulation for validation
            sim_seq = int(time.time() * 1000) % 1_000_000
            sim_tx = f"0.0.{self.config.get('operator_account_id', '9999')}@{int(time.time())}.000000001"
            sim_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
            logger.info(f"[DRY RUN] Anchored dossier {payload['dossier_hash'][:16]} -> Topic {self.topic_id} (SimSeq: {sim_seq})")
            return {
                "sequence_number": sim_seq,
                "tx_id": sim_tx,
                "consensus_timestamp": sim_time,
                "status": "CONFIRMED"
            }"""

new_submit_dry = """        if self.dry_run:
            # Strictly monotonic sequence generation
            sim_seq = self._seq_counter
            self._seq_counter += 1

            op_acc = str(self.config.get('operator_account_id', '0.0.SIMULATED_OPERATOR'))
            if not op_acc.startswith("0.0."):
                op_acc = f"0.0.{op_acc}"

            now_ts = int(time.time())
            sim_tx = f"{op_acc}@{now_ts}.000000001"
            sim_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
            logger.info(f"[SIMULATED_SANDBOX] Anchored dossier {payload['dossier_hash'][:16]} -> Topic {self.topic_id} (MonotonicSeq: {sim_seq})")
            return {
                "sequence_number": sim_seq,
                "tx_id": sim_tx,
                "consensus_timestamp": sim_time,
                "status": "CONFIRMED",
                "mode": "SIMULATED_SANDBOX"
            }"""

if old_submit_dry not in content:
    print("[!] ERROR: Anchor old_submit_dry not found in aw1_hcs_worker.py. Aborting.")
    sys.exit(1)

content = content.replace(old_submit_dry, new_submit_dry, 1)

# Anchor 3: process_pending_batch payload mode update
old_process_update = """            res = hcs_client.submit_attestation(payload)
            with conn.cursor() as cur:
                cur.execute(\"\"\"
                    UPDATE aw1_hcs_anchors
                    SET topic_id = %s,
                        hcs_sequence_number = %s,
                        hcs_tx_id = %s,
                        consensus_timestamp = %s,
                        status = 'CONFIRMED',
                        anchored_at = NOW()
                    WHERE id = %s;
                \"\"\", (topic_id, res["sequence_number"], res["tx_id"], res["consensus_timestamp"], record_id))
                conn.commit()"""

new_process_update = """            res = hcs_client.submit_attestation(payload)
            if "mode" in res:
                payload["mode"] = res["mode"]
            with conn.cursor() as cur:
                cur.execute(\"\"\"
                    UPDATE aw1_hcs_anchors
                    SET topic_id = %s,
                        hcs_sequence_number = %s,
                        hcs_tx_id = %s,
                        consensus_timestamp = %s,
                        attestation_payload = %s,
                        status = 'CONFIRMED',
                        anchored_at = NOW()
                    WHERE id = %s;
                \"\"\", (topic_id, res["sequence_number"], res["tx_id"], res["consensus_timestamp"], json.dumps(payload), record_id))
                conn.commit()"""

if old_process_update not in content:
    print("[!] ERROR: Anchor old_process_update not found in aw1_hcs_worker.py. Aborting.")
    sys.exit(1)

content = content.replace(old_process_update, new_process_update, 1)

# Anchor 4: main() initialization
old_main_init = "    hcs_client = HederaHCSClient(hcs_cfg)"
new_main_init = "    hcs_client = HederaHCSClient(hcs_cfg, db_cfg=db_cfg)"
if old_main_init in content:
    content = content.replace(old_main_init, new_main_init, 1)

with open(WORKER_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("[+] Surgical patch written to aw1_hcs_worker.py.")

# 4. Mandatory Compilation Gate
print("=== MANDATORY COMPILATION GATE ===")
try:
    py_compile.compile(WORKER_FILE, doraise=True)
    print("[✓] Compilation successful: aw1_hcs_worker.py syntax is valid.")
except py_compile.PyCompileError as e:
    print(f"[!] Compilation FAILED: {e}")
    shutil.copyfile(WORKER_BAK, WORKER_FILE)
    print("[-] Reverted to backup.")
    sys.exit(1)
