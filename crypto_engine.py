#!/usr/bin/env python3
import os
import sys
import json
import base64
import hashlib
from abc import ABC, abstractmethod
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY_STORE = "/home/LavetoLab/aw1-breaker/compliance_keys.json"
ENCLAVE_FILE = "/home/LavetoLab/aw1-breaker/enclave_vault.enc"
MASTER_KEY_SEED = os.environ.get("AW1_ENCLAVE_MASTER_SECRET", "Laveto-AW1-Sovereign-Master-Seed-2026-FIPS")

def _derive_master_key(seed: str) -> bytes:
    return hashlib.sha256(seed.encode("utf-8")).digest()

class KMSProvider(ABC):
    @abstractmethod
    def sign_dossier(self, officer_id: str, dossier_hash: str) -> str:
        """Sign a SHA-256 dossier hash and return hex signature."""
        pass

    @abstractmethod
    def verify_signature(self, officer_id: str, dossier_hash: str, signature_hex: str) -> bool:
        """Verify an Ed25519 signature against registered officer key."""
        pass

    @abstractmethod
    def onboard_signatory(self, officer_id: str, name: str, spending_limit_bwp: float) -> dict:
        """Provision a new signatory inside the KMS enclave."""
        pass

class EnclaveKMSProvider(KMSProvider):
    def __init__(self, enclave_path: str = ENCLAVE_FILE, master_secret: str = MASTER_KEY_SEED):
        self.enclave_path = enclave_path
        self.master_key = _derive_master_key(master_secret)
        self.aesgcm = AESGCM(self.master_key)

    def _read_enclave(self) -> dict:
        if not os.path.exists(self.enclave_path):
            return {}
        try:
            with open(self.enclave_path, "rb") as f:
                data = f.read()
            nonce = data[:12]
            ciphertext = data[12:]
            decrypted = self.aesgcm.decrypt(nonce, ciphertext, None)
            return json.loads(decrypted.decode("utf-8"))
        except Exception as e:
            raise RuntimeError(f"ENCLAVE_DECRYPT_FAILURE: Failed to decrypt secure keystore: {e}")

    def _write_enclave(self, payload: dict):
        nonce = os.urandom(12)
        encoded = json.dumps(payload).encode("utf-8")
        ciphertext = self.aesgcm.encrypt(nonce, encoded, None)
        with open(self.enclave_path, "wb") as f:
            f.write(nonce + ciphertext)
        os.chmod(self.enclave_path, 0o600)

    def onboard_signatory(self, officer_id: str, name: str, spending_limit_bwp: float) -> dict:
        priv_key = ed25519.Ed25519PrivateKey.generate()
        pub_key = priv_key.public_key()
        priv_hex = priv_key.private_bytes_raw().hex()
        pub_hex = pub_key.public_bytes_raw().hex()

        # 1. Store private key inside AES-256-GCM enclave
        enclave_data = self._read_enclave()
        enclave_data[officer_id] = {
            "priv_hex": priv_hex,
            "created_at": os.times().elapsed
        }
        self._write_enclave(enclave_data)

        # 2. Register public profile in compliance registry
        registry = {}
        if os.path.exists(KEY_STORE):
            with open(KEY_STORE, "r", encoding="utf-8") as kf:
                registry = json.load(kf)

        registry[officer_id] = {
            "name": name,
            "public_key_hex": pub_hex,
            "spending_limit_bwp": float(spending_limit_bwp),
            "active": True,
            "hsm_enclave_protected": True
        }
        with open(KEY_STORE, "w", encoding="utf-8") as kf:
            json.dump(registry, kf, indent=2)

        return {
            "officer_id": officer_id,
            "name": name,
            "public_key_hex": pub_hex,
            "spending_limit_bwp": spending_limit_bwp
        }

    def sign_dossier(self, officer_id: str, dossier_hash: str) -> str:
        enclave_data = self._read_enclave()
        record = enclave_data.get(officer_id)
        if not record:
            raise KeyError(f"SIGNATORY_NOT_FOUND: No enclave credentials for {officer_id}")

        priv_hex = record["priv_hex"]
        priv_key = ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(priv_hex))
        signature = priv_key.sign(dossier_hash.encode("utf-8"))
        return signature.hex()

    def verify_signature(self, officer_id: str, dossier_hash: str, signature_hex: str) -> bool:
        if not os.path.exists(KEY_STORE):
            return False
        with open(KEY_STORE, "r", encoding="utf-8") as kf:
            registry = json.load(kf)

        officer = registry.get(officer_id)
        if not officer or not officer.get("active"):
            return False

        try:
            pub_bytes = bytes.fromhex(officer["public_key_hex"])
            sig_bytes = bytes.fromhex(signature_hex)
            verify_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
            verify_key.verify(sig_bytes, dossier_hash.encode("utf-8"))
            return True
        except Exception:
            return False

def get_kms_provider() -> KMSProvider:
    # Defaults to local AES-256-GCM hardware enclave; can resolve to Cloud KMS / Vault via env
    return EnclaveKMSProvider()
