import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dialog_mcp.service import Service  # noqa: E402
from dialog_mcp.store import Store  # noqa: E402


def valid_matrix(gate: str = "bestanden") -> dict:
    cell = {"rating": "gut", "note": "geprueft"}
    m = {d: dict(cell) for d in ("sicherheit", "robustheit", "wartbarkeit", "usability")}
    m["compliance"] = {"rating": "gut", "note": "kein Datenabfluss", "gate": gate}
    return m


def valid_post(**overrides) -> dict:
    payload = {
        "body": "Ein Beitrag mit Substanz.",
        "evidence": [{"path": "src/app.py", "locator": "Zeile 12"}],
        "objections": [
            {
                "claim": "Der Hardlink driftet unter NTFS.",
                "reasoning": "Ein Update ersetzt die Datei und erzeugt einen neuen inode.",
                "retract_if": "ein Hash-Vergleich zeigt nach dem Update Gleichheit",
            }
        ],
        "priorities": {"dimensions": ["robustheit"], "sacrifice": "Ich gebe die einfachere Installation auf."},
        "matrix": valid_matrix(),
    }
    payload.update(overrides)
    return payload


def valid_residual() -> dict:
    return {
        "difference": "Ob der Loesungsraum vorab klassifizierbar ist.",
        "why_unresolvable": "Beide Positionen sind widerspruchsfrei und unterscheiden sich nur empirisch.",
        "measurement": "k Sonden je Aufgabe, Artefakt-Divergenz gegen verifizierte Korrektheit.",
    }


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
