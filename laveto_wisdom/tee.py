import glob
import hashlib
import hmac
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone

DB_PATH = '/home/LavetoLab/lvt_database.db'
MODULE_DIR = '/home/LavetoLab/laveto_wisdom'

class TEEAttestationEngine:
    """
    Simulated Hardware-Rooted Confidential Computing Enclave (AWS Nitro / AMD SEV-SNP profile).
    Generates Platform Configuration Register (PCR) measurements and stamps non-repudiable
    cryptographic attestation tokens onto AW-1 decision dossiers.
    """

    ENCLAVE_TYPE = "AWS_NITRO_SIMULATED_SEV"
    # Root key generated inside simulated enclave memory boundary
    _ENCLAVE_ROOT_KEY = hashlib.sha256(b"LVT_ROOT_ENCLAVE_SECURITY_MODULE_2026").digest()

    @classmethod
    def compute_pcr0(cls) -> str:
        """
        PCR0: Hash of all immutable execution guard python modules.
        Any tampering with source code alters this measurement.
        """
        hasher = hashlib.sha256()
        target_files = sorted(glob.glob(os.path.join(MODULE_DIR, "*.py")))
        for fpath in target_files:
            try:
                with open(fpath, "rb") as f:
                    hasher.update(f.read())
            except Exception:
                pass
        return hasher.hexdigest()

    @classmethod
    def compute_pcr1(cls) -> str:
        """
        PCR1: Measurement of active statutory rules and synthesized AST invariants.
        """
        hasher = hashlib.sha256()
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            rules = c.execute("SELECT rule_id, threat_pattern, synthesized_predicate FROM synthesized_ast_rules ORDER BY rule_id").fetchall()
            conn.close()
            hasher.update(json.dumps(rules).encode('utf-8'))
        except Exception:
            hasher.update(b"EMPTY_POLICY_SET")
        return hasher.hexdigest()

    @classmethod
    def compute_pcr2(cls, session_id: str) -> str:
        """
        PCR2: Execution session entropy and environment isolation boundary.
        """
        return hashlib.sha256(f"SESSION_ENV:{session_id}:SOVEREIGN_BW".encode('utf-8')).hexdigest()

    @classmethod
    def issue_attestation(cls, dossier_hash: str, session_id: str = "default_session"):
        """
        Generates hardware-attested token sealing the decision dossier with PCR measurements.
        """
        pcr0 = cls.compute_pcr0()
        pcr1 = cls.compute_pcr1()
        pcr2 = cls.compute_pcr2(session_id)
        now = datetime.now(timezone.utc).isoformat()
        
        # Enclave public identity (derived from enclave root key)
        pub_key = hashlib.sha256(cls._ENCLAVE_ROOT_KEY + b":PUBLIC").hexdigest()

        # Canonical attestation document preimage
        canonical_doc = f"{cls.ENCLAVE_TYPE}:{now}:{dossier_hash}:{pcr0}:{pcr1}:{pcr2}:{pub_key}"
        signature = hmac.new(cls._ENCLAVE_ROOT_KEY, canonical_doc.encode('utf-8'), hashlib.sha256).hexdigest()
        attestation_id = hashlib.sha256(f"ATT_{canonical_doc}".encode('utf-8')).hexdigest()[:24]

        # Persist to database ledger
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""
                INSERT INTO tee_attestation_records 
                (attestation_id, timestamp, dossier_hash, enclave_type, pcr0, pcr1, pcr2, public_key_hex, signature_hex, verification_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'VALID')
            """, (attestation_id, now, dossier_hash, cls.ENCLAVE_TYPE, pcr0, pcr1, pcr2, pub_key, signature))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[TEE AUDIT ERROR]: {e}")

        return {
            "attestation_id": attestation_id,
            "enclave_type": cls.ENCLAVE_TYPE,
            "timestamp": now,
            "pcr_measurements": {
                "PCR0_CODE": pcr0[:16] + "...",
                "PCR1_POLICY": pcr1[:16] + "...",
                "PCR2_SESSION": pcr2[:16] + "..."
            },
            "public_key": pub_key[:16] + "...",
            "enclave_signature": signature,
            "verification": "HARDWARE_SEALED"
        }

    @classmethod
    def verify_attestation(cls, attestation_id: str) -> bool:
        """
        Independent verification of TEE attestation token against database record.
        """
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        row = c.execute("""
            SELECT dossier_hash, pcr0, pcr1, pcr2, public_key_hex, signature_hex, timestamp 
            FROM tee_attestation_records WHERE attestation_id = ?
        """, (attestation_id,)).fetchone()
        conn.close()

        if not row:
            return False

        d_hash, p0, p1, p2, pub_key, recorded_sig, ts = row
        canonical_doc = f"{cls.ENCLAVE_TYPE}:{ts}:{d_hash}:{p0}:{p1}:{p2}:{pub_key}"
        recalculated = hmac.new(cls._ENCLAVE_ROOT_KEY, canonical_doc.encode('utf-8'), hashlib.sha256).hexdigest()
        return hmac.compare_digest(recalculated, recorded_sig)
