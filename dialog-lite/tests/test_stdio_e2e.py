"""End-to-End ueber stdio mit zwei echten Prozessen auf einem Ordner.

Zwei getrennte Serverprozesse, verschiedene `--as`-Namen, dieselbe Datei -
also genau der Aufbau, in dem die zweite Variante spaeter laeuft.
"""

import json
import os
import sys
from pathlib import Path

import pytest
from lite_helpers import A, B

SRC = str(Path(__file__).resolve().parents[1] / "src")


@pytest.fixture
def anyio_backend():
    return "asyncio"


class ToolFailed(RuntimeError):
    """Werkzeugfehler, so wie ihn der Agent zu sehen bekommt."""


async def call(directory: str, who: str, tool: str, args: dict):
    from mcp import StdioServerParameters
    from mcp.client import Client

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "dialog_lite", "--as", who, "--dir", directory],
        env={**os.environ, "PYTHONPATH": SRC},
    )
    error = payload = None
    # Fehler erst ausserhalb der Task-Group werfen, sonst verpackt anyio ihn.
    async with Client(params) as client:
        result = await client.call_tool(tool, args)
        if result.is_error:
            error = result.content[0].text
        elif result.structured_content is not None:
            payload = result.structured_content
        else:
            payload = json.loads(result.content[0].text)
    if error is not None:
        raise ToolFailed(error)
    # Ein Werkzeug, das eine Liste liefert, kommt laut MCP als {"result": [...]} zurueck.
    if isinstance(payload, dict) and set(payload) == {"result"}:
        return payload["result"]
    return payload


@pytest.mark.anyio
async def test_two_processes_share_one_dialogue(tmp_path):
    d = str(tmp_path)
    await call(d, A, "dialog_open", {"slug": "e2e", "topic": "Allowlist statt Denylist", "partner": B, "max_rounds": 2})

    await call(d, A, "dialog_probe", {"slug": "e2e", "artifact": "export.ps1:44 — Denylist laesst .pem durch"})
    verdeckt = await call(d, B, "dialog_read", {"slug": "e2e"})
    assert verdeckt["probes"] is None
    assert "export.ps1" not in json.dumps(verdeckt, ensure_ascii=False)

    await call(d, B, "dialog_probe", {"slug": "e2e", "artifact": "install.ps1:12 — Hardlink driftet"})
    status = await call(d, B, "dialog_probe_resolve", {
        "slug": "e2e", "outcome": "diverged", "rationale": "Zwei verschiedene Stellen benannt."})
    assert status["state"] == "debating" and status["turn"] == A

    with pytest.raises(ToolFailed, match="ist am Zug"):
        await call(d, B, "dialog_post", {"slug": "e2e", "body": "vorgedraengelt"})

    with pytest.raises(ToolFailed, match="Ruecknahmebedingung"):
        await call(d, A, "dialog_post", {
            "slug": "e2e", "body": "Text",
            "objections": [{"claim": "Das ist schlecht.", "retract_if": ""}]})

    await call(d, A, "dialog_post", {
        "slug": "e2e", "body": "Denylist ist strukturell fragil.",
        "objections": [{"claim": "Neue Secret-Formate rutschen durch.",
                        "retract_if": "ein Test alle bekannten Endungen abdeckt"}]})
    await call(d, B, "dialog_post", {"slug": "e2e", "body": "Zugestanden, aber Allowlist bremst neue Dateitypen."})
    await call(d, A, "dialog_post", {"slug": "e2e", "body": "Dann eben Allowlist mit dokumentierter Freigabe."})
    last = await call(d, B, "dialog_post", {"slug": "e2e", "body": "Einverstanden."})
    assert last["turn"] is None

    done = await call(d, A, "dialog_close", {"slug": "e2e", "summary": "Allowlist beschlossen."})
    assert done["state"] == "done"

    page = (tmp_path / "e2e.html").read_text(encoding="utf-8")
    assert "Allowlist beschlossen." in page
    assert 'http-equiv="refresh"' not in page
    assert "Hardlink driftet" in page  # Sonden jetzt sichtbar


@pytest.mark.anyio
async def test_matching_probes_skip_the_debate(tmp_path):
    d = str(tmp_path)
    await call(d, A, "dialog_open", {"slug": "klar", "topic": "Offensichtlicher Fall", "partner": B})
    for who in (A, B):
        await call(d, who, "dialog_probe", {"slug": "klar", "artifact": "install.ps1:12 — Hardlink driftet"})
    status = await call(d, B, "dialog_probe_resolve", {
        "slug": "klar", "outcome": "converged", "rationale": "Beide dieselbe Stelle."})
    assert status["state"] == "done" and status["round"] == 1

    listing = await call(d, A, "dialog_list", {})
    assert [t["slug"] for t in listing] == ["klar"]
