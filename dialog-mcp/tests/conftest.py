import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dialog_mcp.service import Service  # noqa: E402
from dialog_mcp.store import Store  # noqa: E402
from mcp_helpers import valid_post, valid_residual  # noqa: E402,F401


@pytest.fixture
def service(tmp_path) -> Service:
    store = Store(":memory:")
    store.upsert_participant("claude", "Claude Code", "debater", "h-claude")
    store.upsert_participant("ag", "Antigravity", "debater", "h-ag")
    store.upsert_participant("sts", "Steffen", "owner", "h-sts", is_human=True)
    store.upsert_participant("gast", "Gast", "prober", "h-gast")
    return Service(store, export_dir=str(tmp_path / "dialog"))


@pytest.fixture
def debating(service) -> Service:
    """Thread, dessen Sondenphase divergent ausgegangen ist."""
    service.open_thread("sts", slug="t", topic="Testthema", debaters=["claude", "ag"], max_rounds=3)
    service.submit_probe("claude", "t", "src/a.py:12 ist die Ursache", [{"path": "src/a.py", "locator": "12"}])
    service.submit_probe("ag", "t", "src/b.py:40 ist die Ursache", [{"path": "src/b.py", "locator": "40"}])
    service.resolve_probes("claude", "t", "diverged", "Verschiedene Stellen benannt.")
    return service
