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


# =====================================================================
# Enterprise Policy-as-Code Engine (Declarative AST Inspection)
# =====================================================================
import ast, json, os, time
from typing import Dict, Optional, Set, Tuple

DEFAULT_POLICY = {
    "version": "1.0",
    "policy_name": "enterprise-standard",
    "enforcement_mode": "FAIL_CLOSED",
    "prohibited_modules": ["subprocess", "shutil", "pty", "socket", "ctypes", "multiprocessing", "threading"],
    "prohibited_calls": ["system", "popen", "spawn", "fork", "execv", "execve", "kill", "remove", "unlink", "rmdir"],
    "prohibited_builtins": ["eval", "exec", "compile", "__import__"],
    "prohibited_attributes": ["__subclasses__", "__globals__", "__code__", "__builtins__", "__bases__", "__mro__"],
    "limits": {"max_node_count": 1500, "max_ast_depth": 25, "max_payload_bytes": 65536},
    "strict_allowlist_mode": False,
    "allowed_modules": ["math", "json", "re", "datetime", "typing", "dataclasses", "collections"]
}

class SecurityPolicy:
    def __init__(self, policy_data: Optional[Dict] = None, policy_path: Optional[str] = None):
        self.policy_path = policy_path
        self._last_loaded_mtime = 0.0
        self.load(policy_data or DEFAULT_POLICY)

    def load(self, data: Dict) -> None:
        self.version = data.get("version", "1.0")
        self.policy_name = data.get("policy_name", "custom")
        self.enforcement_mode = data.get("enforcement_mode", "FAIL_CLOSED")
        self.prohibited_modules: Set[str] = set(data.get("prohibited_modules", []))
        self.prohibited_calls: Set[str] = set(data.get("prohibited_calls", []))
        self.prohibited_builtins: Set[str] = set(data.get("prohibited_builtins", []))
        self.prohibited_attributes: Set[str] = set(data.get("prohibited_attributes", []))
        self.strict_allowlist_mode: bool = data.get("strict_allowlist_mode", False)
        self.allowed_modules: Set[str] = set(data.get("allowed_modules", []))
        limits = data.get("limits", {})
        self.max_node_count = limits.get("max_node_count", 1500)
        self.max_ast_depth = limits.get("max_ast_depth", 25)
        self.max_payload_bytes = limits.get("max_payload_bytes", 65536)

    def reload_if_modified(self) -> bool:
        if not self.policy_path or not os.path.exists(self.policy_path): return False
        mtime = os.path.getmtime(self.policy_path)
        if mtime > self._last_loaded_mtime:
            try:
                with open(self.policy_path, "r", encoding="utf-8") as f: self.load(json.load(f))
                self._last_loaded_mtime = mtime
                return True
            except Exception: return False
        return False

    def inspect_ast(self, code_str: str) -> Tuple[bool, Optional[str]]:
        if len(code_str.encode("utf-8")) > self.max_payload_bytes:
            return False, f"Payload size exceeds {self.max_payload_bytes} bytes"
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return False, f"Syntax parse failure: {e}"
        nodes, stack = 0, [(tree, 1)]
        while stack:
            node, depth = stack.pop()
            nodes += 1
            if nodes > self.max_node_count: return False, f"AST complexity: exceeded {self.max_node_count} nodes"
            if depth > self.max_ast_depth: return False, f"AST complexity: exceeded {self.max_ast_depth} nesting levels"
            if isinstance(node, ast.Import):
                for alias in node.names:
                    pkg = alias.name.split(".")[0]
                    if self.strict_allowlist_mode and pkg not in self.allowed_modules:
                        return False, f"Strict allowlist violation: module '{pkg}' not permitted"
                    if pkg in self.prohibited_modules: return False, f"Prohibited module import: {pkg}"
            elif isinstance(node, ast.ImportFrom) and node.module:
                pkg = node.module.split(".")[0]
                if self.strict_allowlist_mode and pkg not in self.allowed_modules:
                    return False, f"Strict allowlist violation: module '{pkg}' not permitted"
                if pkg in self.prohibited_modules: return False, f"Prohibited module import: {pkg}"
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in self.prohibited_builtins:
                    return False, f"Prohibited built-in invocation: {node.func.id}"
                elif isinstance(node.func, ast.Attribute) and node.func.attr in self.prohibited_calls:
                    return False, f"Prohibited function invocation: {node.func.attr}"
            elif isinstance(node, ast.Attribute) and node.attr in self.prohibited_attributes:
                return False, f"Prohibited dunder attribute access: {node.attr}"
            for child in ast.iter_child_nodes(node):
                stack.append((child, depth + 1))
        return True, None

_GLOBAL_POLICY = SecurityPolicy()

def get_active_policy() -> SecurityPolicy:
    global _GLOBAL_POLICY
    _GLOBAL_POLICY.reload_if_modified()
    return _GLOBAL_POLICY

def configure_policy(policy_data: Optional[Dict] = None, policy_file: Optional[str] = None) -> SecurityPolicy:
    global _GLOBAL_POLICY
    if policy_file and os.path.exists(policy_file):
        with open(policy_file, "r", encoding="utf-8") as f:
            _GLOBAL_POLICY = SecurityPolicy(json.load(f), policy_path=policy_file)
            _GLOBAL_POLICY._last_loaded_mtime = os.path.getmtime(policy_file)
    elif policy_data:
        _GLOBAL_POLICY = SecurityPolicy(policy_data)
    return _GLOBAL_POLICY
