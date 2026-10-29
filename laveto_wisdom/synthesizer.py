import ast
import hashlib
import sqlite3
from datetime import datetime, timezone

DB_PATH = '/home/LavetoLab/lvt_database.db'

class RuleSynthesizer:
    """
    Analyzes evasive payload patterns, synthesizes deterministic AST node
    predicates, and persists hot-patchable grammar invariants.
    """

    _RULE_CACHE = []
    _LAST_LOADED = None

    @classmethod
    def load_active_rules(cls, force=False):
        if cls._RULE_CACHE and not force:
            return cls._RULE_CACHE
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        rows = c.execute("""
            SELECT rule_id, rule_name, threat_pattern, target_node, synthesized_predicate, action 
            FROM synthesized_ast_rules WHERE status = 'ACTIVE'
        """).fetchall()
        conn.close()

        cls._RULE_CACHE = [
            {
                "rule_id": r[0],
                "rule_name": r[1],
                "pattern": r[2],
                "target_node": r[3],
                "predicate": r[4],
                "action": r[5]
            }
            for r in rows
        ]
        return cls._RULE_CACHE

    @classmethod
    def analyze_and_synthesize(cls, code_str: str):
        """
        Scans AST for novel evasion patterns and synthesizes an invariant rule.
        """
        try:
            tree = ast.parse(code_str)
        except Exception:
            return None

        synthesized = None

        for node in ast.walk(tree):
            # Pattern A: Dynamic builtin extraction via getattr (e.g., getattr(__builtins__, 'eval'))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'getattr':
                if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                    target_attr = str(node.args[1].value)
                    if target_attr in {'eval', 'exec', '__import__', 'system', 'popen'}:
                        synthesized = {
                            "name": f"RULE_FORBID_GETATTR_{target_attr.upper()}",
                            "pattern": f"DYNAMIC_GETATTR_BUILTIN_{target_attr.upper()}",
                            "target_node": "Call",
                            "predicate": f"node.func.id == 'getattr' and node.args[1].value == '{target_attr}'"
                        }
                        break

            # Pattern B: Base64 unpacking wrapped in eval/exec
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in {'b64decode', 'decode'} and any(
                    isinstance(parent, ast.Call) and getattr(parent.func, 'id', '') in {'eval', 'exec'}
                    for parent in ast.walk(tree)
                ):
                    synthesized = {
                        "name": "RULE_FORBID_BASE64_EVAL_CHAIN",
                        "pattern": "BASE64_INDIRECT_EXEC",
                        "target_node": "Call",
                        "predicate": "node.func.attr in ('b64decode', 'decode')"
                    }
                    break

        if synthesized:
            return cls._persist_synthesized_rule(synthesized)
        return None

    @classmethod
    def _persist_synthesized_rule(cls, rule_data):
        now = datetime.now(timezone.utc).isoformat()
        rule_id = hashlib.sha256(f"{rule_data['name']}:{now}".encode('utf-8')).hexdigest()[:16]

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT OR IGNORE INTO synthesized_ast_rules 
            (rule_id, rule_name, threat_pattern, target_node, synthesized_predicate, action, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'TRIP_CANARY', 'ACTIVE', ?)
        """, (rule_id, rule_data['name'], rule_data['pattern'], rule_data['target_node'], rule_data['predicate'], now))
        conn.commit()
        conn.close()

        # Invalidate in-memory cache to hot-patch instantly
        cls.load_active_rules(force=True)
        return rule_id
