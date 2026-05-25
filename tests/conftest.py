import sys
from pathlib import Path

import pytest

# Repo root (parent of tests/) must be on path for `api` and `engine` imports.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


@pytest.fixture(scope="session", autouse=True)
def _init_test_db():
    from api.database import init_db

    init_db()
