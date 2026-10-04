import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aw1.memory import StatefulCausalMemory

class AWStatefulCausalMemory(StatefulCausalMemory):
    """Compatibility wrapper exposing StatefulCausalMemory as AWStatefulCausalMemory."""
    pass
