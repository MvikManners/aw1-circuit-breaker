import re
from typing import Optional, Tuple

class SQLGuard:
    SQL_DESTRUCTIVE_PATTERNS = [
        (re.compile(r'\bDROP\s+(TABLE|DATABASE|SCHEMA|VIEW)\b', re.I), "[SQL_DROP_OBJECT]"),
        (re.compile(r'\bTRUNCATE\s+(TABLE)?\b', re.I), "[SQL_TRUNCATE]"),
        (re.compile(r'\bDELETE\s+FROM\b\s+(?!.*\bWHERE\b)', re.I), "[SQL_DELETE_ALL]"),
        (re.compile(r'\bALTER\s+TABLE\b.*\bDROP\b', re.I), "[SQL_ALTER_DROP]"),
        (re.compile(r'\bGRANT\s+ALL\b', re.I), "[SQL_PRIVILEGE_ESCALATION]"),
    ]

    @classmethod
    def inspect(cls, payload: str) -> Optional[Tuple[str, str]]:
        clean = payload.strip()
        for pattern, primitive in cls.SQL_DESTRUCTIVE_PATTERNS:
            if pattern.search(clean):
                return primitive, f"Destructive SQL statement detected matching primitive {primitive}"
        return None
