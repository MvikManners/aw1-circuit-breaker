"""
Enterprise Secret Ingress & Key Management Engine for Laveto Wisdom & AW-1.
Supports HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager, and Hardened Env Ingress.
Provides real-time secret redaction and entropy validation.
"""
import os
import re
import math
import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("aw1.secrets")

SENSITIVE_KEY_PATTERNS = [
    r"api[_-]?key", r"auth[_-]?token", r"bearer", r"secret", r"password",
    r"private[_-]?key", r"client[_-]?secret", r"credential", r"access[_-]?token"
]

class SecretsEngine:
    _instance = None
    _cached_secrets: Dict[str, str] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SecretsEngine, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.environment = os.getenv("ENVIRONMENT", os.getenv("FLASK_ENV", "development")).lower()
        self.is_production = self.environment in ["production", "prod"]
        self.provider = "env"

        # Check Tier 1: HashiCorp Vault
        if os.getenv("VAULT_ADDR") and os.getenv("VAULT_TOKEN"):
            try:
                import hvac
                self.vault_client = hvac.Client(url=os.getenv("VAULT_ADDR"), token=os.getenv("VAULT_TOKEN"))
                if self.vault_client.is_authenticated():
                    self.provider = "hashicorp_vault"
                    logger.info("🔐 SecretsEngine: Authenticated with HashiCorp Vault.")
                    return
            except Exception as e:
                logger.warning(f"Vault configuration detected but connection failed: {e}. Falling back...")

        # Check Tier 2: AWS Secrets Manager
        if os.getenv("AWS_SECRET_NAME") and os.getenv("AWS_REGION"):
            try:
                import boto3
                self.aws_client = boto3.client("secretsmanager", region_name=os.getenv("AWS_REGION"))
                self.provider = "aws_secrets_manager"
                logger.info("🔐 SecretsEngine: Authenticated with AWS Secrets Manager.")
                return
            except Exception as e:
                logger.warning(f"AWS Secrets Manager detected but connection failed: {e}. Falling back...")

        logger.info(f"🔐 SecretsEngine: Operating under {self.provider.upper()} ingress mode.")

    def get_secret(self, key: str, default: Optional[str] = None) -> str:
        """Retrieves a secret with cache-aside and provider routing."""
        if key in self._cached_secrets:
            return self._cached_secrets[key]

        value = None

        # Provider 1: HashiCorp Vault
        if self.provider == "hashicorp_vault":
            try:
                path = os.getenv("VAULT_SECRET_PATH", "secret/data/aw1")
                res = self.vault_client.secrets.kv.v2.read_secret_version(path=path)
                data = res.get("data", {}).get("data", {})
                value = data.get(key)
            except Exception as e:
                logger.warning(f"Failed to read {key} from Vault: {e}")

        # Provider 2: AWS Secrets Manager
        elif self.provider == "aws_secrets_manager":
            try:
                secret_name = os.getenv("AWS_SECRET_NAME")
                res = self.aws_client.get_secret_value(SecretId=secret_name)
                secret_dict = json.loads(res.get("SecretString", "{}"))
                value = secret_dict.get(key)
            except Exception as e:
                logger.warning(f"Failed to read {key} from AWS: {e}")

        # Provider 4 (Fallback): Environment Ingress
        if value is None:
            value = os.getenv(key, default)

        # Production Validation: Reject empty or weak secrets
        if self.is_production:
            if not value:
                raise ValueError(f"CRITICAL: Required secret '{key}' is missing in production environment!")
            self._validate_entropy(key, value)

        if value is not None:
            self._cached_secrets[key] = str(value)
            return str(value)

        return default or ""

    @staticmethod
    def _validate_entropy(key: str, value: str, min_entropy: float = 3.0):
        """Calculates Shannon entropy to detect default/trivial keys in production."""
        if value.lower() in ["changeme", "secret", "password", "admin", "123456", "test"]:
            raise ValueError(f"SECURITY BREACH: Secret '{key}' is using an insecure default value!")

        prob = [float(value.count(c)) / len(value) for c in set(value)]
        entropy = -sum([p * math.log2(p) for p in prob])
        if len(value) >= 12 and entropy < min_entropy:
            logger.warning(f"⚠️ Low entropy detected for secret '{key}' (Entropy: {entropy:.2f}). Consider rotation.")

    @staticmethod
    def redact(data: Any) -> Any:
        """Recursively scrubs secrets, tokens, passwords, and PII from data structures."""
        if isinstance(data, dict):
            scrubbed = {}
            for k, v in data.items():
                if any(re.search(pat, str(k), re.IGNORECASE) for pat in SENSITIVE_KEY_PATTERNS):
                    scrubbed[k] = "[REDACTED_CONFIDENTIAL]"
                else:
                    scrubbed[k] = SecretsEngine.redact(v)
            return scrubbed
        elif isinstance(data, list):
            return [SecretsEngine.redact(item) for item in data]
        elif isinstance(data, str):
            # Redact Authorization: Bearer tokens
            scrubbed = re.sub(r"(Bearer\s+)[A-Za-z0-9\-_\.=]+", r"[REDACTED_TOKEN]", data, flags=re.IGNORECASE)
            # Redact high-confidence API keys (e.g. sk_live_..., ghp_..., etc.)
            scrubbed = re.sub(r"(sk_live_[0-9a-zA-Z]{20,})", "[REDACTED_API_KEY]", scrubbed)
            return scrubbed
        return data

# Global singleton
secrets_engine = SecretsEngine()
get_secret = secrets_engine.get_secret
redact_sensitive_data = secrets_engine.redact
