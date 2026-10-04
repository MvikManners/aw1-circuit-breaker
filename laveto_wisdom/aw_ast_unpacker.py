import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aw1.unpacker import ASTSymbolicUnpacker

class AWASTUnpacker(ASTSymbolicUnpacker):
    """Compatibility wrapper exposing ASTSymbolicUnpacker as AWASTUnpacker."""
    pass
