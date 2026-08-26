import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dialog_lite import thread  # noqa: E402

from lite_helpers import A, B  # noqa: E402


@pytest.fixture
def d(tmp_path) -> str:
    return str(tmp_path)


@pytest.fixture
def debating(d) -> str:
    """Thread, dessen Sondenphase divergent ausgegangen ist."""
    thread.open_thread(d, me=A, slug="t", topic="Testthema", partner=B, max_rounds=3)
    thread.submit_probe(d, me=A, slug="t", artifact="src/a.py:12")
    thread.submit_probe(d, me=B, slug="t", artifact="src/b.py:40")
    thread.resolve_probes(d, me=A, slug="t", outcome="diverged", rationale="Verschiedene Stellen.")
    return d

