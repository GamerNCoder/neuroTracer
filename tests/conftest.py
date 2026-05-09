import sys
from pathlib import Path

# Repo root (parent of tests/) must be on path for `api` and `engine` imports.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
