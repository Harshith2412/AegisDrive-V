import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "sim") not in sys.path:
    sys.path.insert(0, str(ROOT / "sim"))
SCENARIOS = ROOT / "scenarios"
