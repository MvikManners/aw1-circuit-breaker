import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import sys
from pathlib import Path

# Bridge aw1-breaker path if not in site-packages
for p in ['/home/LavetoLab/aw1-breaker', '/home/LavetoLab']:
    if p not in sys.path and Path(p).exists():
        sys.path.insert(0, p)

try:
    from aw1.unpacker import ASTSymbolicUnpacker
except ImportError:
    class ASTSymbolicUnpacker:
        """Standalone fallback symbolic unpacker for AW-1 AST trees."""
        def __init__(self, *args, **kwargs):
            pass
        def unpack(self, code_str):
            import ast
            return ast.parse(code_str)


class AWASTUnpacker(ASTSymbolicUnpacker):
    """Compatibility wrapper exposing ASTSymbolicUnpacker as AWASTUnpacker."""
    pass
