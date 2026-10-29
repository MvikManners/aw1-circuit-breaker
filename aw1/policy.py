from dataclasses import dataclass, field
from typing import Set

@dataclass
class PolicyConfig:
    name: str = "enterprise_default"
    critical_targets: Set[str] = field(default_factory=lambda: {
        # Financial
        "hot_wallet", "core_ledger", "treasury", "vault", "reserve",
        # Cloud & Infra
        "s3://", "production", "kube-system", "/etc/", "/root", "/proc",
        # Healthcare & PII
        "patient", "medical_record", "ssn", "credit_card", "password"
    })
    restricted_actions: Set[str] = field(default_factory=lambda: {
        "drain", "transfer", "disburse", "withdraw",
        "drop", "truncate", "delete", "rmtree", "exfiltrate", "dump",
        "export", "fetch_all"
    })
    strict_sql: bool = True
    strict_shell: bool = True

    @classmethod
    def fintech(cls):
        return cls(name="fintech")

    @classmethod
    def healthcare(cls):
        return cls(
            name="healthcare",
            critical_targets={"patient", "medical_record", "hipaa", "ehr", "diagnosis"},
            restricted_actions={"export", "dump", "exfiltrate", "delete", "fetch_all"}
        )

    @classmethod
    def cloud_infra(cls):
        return cls(
            name="cloud_infra",
            critical_targets={"s3://", "aws_iam", "kubernetes", "production_db"},
            restricted_actions={"destroy", "terminate", "rmtree", "delete", "drop"}
        )
