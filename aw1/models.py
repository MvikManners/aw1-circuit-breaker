from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass(frozen=True)
class Verdict:
    decision: str
    status: str
    containment_reason: str
    ast_primitives: List[str] = field(default_factory=list)
    latency_ms: float = 0.0
    sha256_dossier: str = ""
    token: Optional[str] = None

    @property
    def is_permitted(self) -> bool:
        return self.status == "PERMITTED"

    @property
    def is_contained(self) -> bool:
        return self.status == "HALT_AND_CONTAIN"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision,
            "status": self.status,
            "containment_reason": self.containment_reason,
            "ast_primitives": self.ast_primitives,
            "latency_ms": self.latency_ms,
            "sha256_dossier": self.sha256_dossier,
            "token": self.token
        }

    # Backward compatibility with dictionary access
    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def get(self, item: str, default: Any = None) -> Any:
        return getattr(self, item, default)

    def keys(self):
        return self.to_dict().keys()

    def values(self):
        return self.to_dict().values()

    def items(self):
        return self.to_dict().items()

    def __contains__(self, item: str) -> bool:
        return hasattr(self, item)
