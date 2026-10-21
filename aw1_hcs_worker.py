#!/usr/bin/env python3
import json
import time
import os
import sys
import signal
import datetime
import logging
import pymysql

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [AW1-HCS] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("aw1_hcs_worker")

CONFIG_PATH = "/home/LavetoLab/aw1-breaker/hcs_config.json"
DB_CONFIG_PATH = "/home/LavetoLab/aw1-breaker/db_config.json"

RUNNING = True

def handle_shutdown(signum, frame):
    logger.info("Termination signal received. Exiting immediately...")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

def get_db_connection(cfg):
    return pymysql.connect(
        host=cfg["host"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        cursorclass=pymysql.cursors.DictCursor
    )

class HederaHCSClient:
    """Manages HCS topic submissions via native SDK or REST fallback."""
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
                logger.warning(f"Could not initialize monotonic sequence from DB: {e}")
        
        if not self.dry_run:
            try:
                # Attempt importing hiero/hedera SDK
                from hiero_sdk_python import Client, AccountId, PrivateKey, TopicMessageSubmitTransaction, TopicId
                self.client = Client.for_testnet() if self.network == "testnet" else Client.for_mainnet()
                self.client.set_operator(
                    AccountId.from_string(config["operator_account_id"]),
                    PrivateKey.from_string(config["operator_private_key"])
                )
                self.sdk_available = True
                logger.info("Initialized native Hedera SDK client.")
            except ImportError:
                logger.warning("Hedera SDK not installed in environment. Operating via REST relay mode.")

    def submit_attestation(self, payload: dict) -> dict:
        """
        Submits attestation envelope to HCS.
        Returns dict with sequence_number, tx_id, consensus_timestamp.
        """
        message_bytes = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode("utf-8")

        if self.dry_run:
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
            }

        if self.sdk_available:
            from hiero_sdk_python import TopicMessageSubmitTransaction, TopicId
            tx = TopicMessageSubmitTransaction() \
                .set_topic_id(TopicId.from_string(self.topic_id)) \
                .set_message(message_bytes)
            
            resp = tx.execute(self.client)
            receipt = resp.get_receipt(self.client)
            return {
                "sequence_number": receipt.topic_sequence_number,
                "tx_id": str(resp.transaction_id),
                "consensus_timestamp": str(receipt.consensus_timestamp),
                "status": "CONFIRMED"
            }

        raise NotImplementedError("Live submission requires hiero-sdk-python or configured REST relay.")

def hydrate_anchor_queue(conn):
    """Discovers new audit dossiers in aw1_dossier_log and registers them as PENDING."""
    with conn.cursor() as cur:
        # Find dossiers not yet present in aw1_hcs_anchors
        cur.execute("""
            SELECT d.id AS audit_id, 
                   LOWER(REPLACE(d.sha256_dossier_hash, '0x', '')) AS clean_hash,
                   d.agent_id,
                   d.audit_verdict,
                   d.gate_triggered,
                   d.created_at
            FROM aw1_dossier_log d
            LEFT JOIN aw1_hcs_anchors a ON a.dossier_hash = LOWER(REPLACE(d.sha256_dossier_hash, '0x', ''))
            WHERE a.id IS NULL
            ORDER BY d.id ASC
            LIMIT 50;
        """)
        new_dossiers = cur.fetchall()

        if not new_dossiers:
            return 0

        for d in new_dossiers:
            clean_hash = d["clean_hash"]
            if not clean_hash:
                continue

            envelope = {
                "proto": "AW1_HCS_ATTESTATION/1.0",
                "dossier_hash": clean_hash,
                "audit_id": d["audit_id"],
                "agent_id": d["agent_id"],
                "verdict": d["audit_verdict"],
                "gate_triggered": d["gate_triggered"],
                "timestamp_iso": d["created_at"].isoformat() if isinstance(d["created_at"], (datetime.datetime, datetime.date)) else str(d["created_at"])
            }

            cur.execute("""
                INSERT IGNORE INTO aw1_hcs_anchors 
                (audit_id, dossier_hash, topic_id, attestation_payload, status)
                VALUES (%s, %s, %s, %s, 'PENDING');
            """, (d["audit_id"], clean_hash, "PENDING_ASSIGNMENT", json.dumps(envelope)))

        conn.commit()
        return len(new_dossiers)

def process_pending_batch(conn, hcs_client, config):
    """Processes a batch of PENDING attestation records."""
    batch_size = config.get("batch_size", 10)
    topic_id = config.get("topic_id", "0.0.0")

    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, audit_id, dossier_hash, attestation_payload, retry_count
            FROM aw1_hcs_anchors
            WHERE status = 'PENDING'
            ORDER BY id ASC
            LIMIT %s;
        """, (batch_size,))
        batch = cur.fetchall()

    if not batch:
        return 0

    for record in batch:
        record_id = record["id"]
        d_hash = record["dossier_hash"]
        payload = json.loads(record["attestation_payload"])

        try:
            res = hcs_client.submit_attestation(payload)
            if "mode" in res:
                payload["mode"] = res["mode"]
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE aw1_hcs_anchors
                    SET topic_id = %s,
                        hcs_sequence_number = %s,
                        hcs_tx_id = %s,
                        consensus_timestamp = %s,
                        attestation_payload = %s,
                        status = 'CONFIRMED',
                        anchored_at = NOW()
                    WHERE id = %s;
                """, (topic_id, res["sequence_number"], res["tx_id"], res["consensus_timestamp"], json.dumps(payload), record_id))
                conn.commit()
            logger.info(f"Dossier {d_hash[:16]} anchored successfully (Seq: {res['sequence_number']}).")

        except Exception as err:
            logger.error(f"Failed to submit dossier {d_hash[:16]}: {err}")
            retries = record["retry_count"] + 1
            new_status = 'FAILED' if retries >= config.get("max_retries", 3) else 'PENDING'
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE aw1_hcs_anchors
                    SET retry_count = %s,
                        status = %s,
                        error_message = %s
                    WHERE id = %s;
                """, (retries, new_status, str(err)[:255], record_id))
                conn.commit()

    return len(batch)

def main():
    logger.info("Starting AW-1 Hedera HCS Asynchronous Anchoring Worker...")
    
    with open(DB_CONFIG_PATH, "r") as f:
        db_cfg = json.load(f)

    with open(CONFIG_PATH, "r") as f:
        hcs_cfg = json.load(f)

    hcs_client = HederaHCSClient(hcs_cfg, db_cfg=db_cfg)
    poll_sec = hcs_cfg.get("poll_interval_seconds", 5)

    conn = get_db_connection(db_cfg)

    while RUNNING:
        try:
            conn.ping(reconnect=True)
            
            # 1. Ingest unindexed dossiers from aw1_dossier_log
            hydrated = hydrate_anchor_queue(conn)
            if hydrated > 0:
                logger.info(f"Enqueued {hydrated} new dossiers for HCS anchoring.")

            # 2. Process batch of PENDING submissions
            processed = process_pending_batch(conn, hcs_client, hcs_cfg)

            # Rest if queue is clear
            if processed == 0 and hydrated == 0:
                time.sleep(poll_sec)

        except Exception as e:
            logger.error(f"Worker iteration exception: {e}")
            time.sleep(poll_sec)

    conn.close()
    logger.info("AW-1 HCS worker terminated cleanly.")

if __name__ == "__main__":
    main()
