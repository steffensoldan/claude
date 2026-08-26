"""End-to-End ueber echtes HTTP: zwei Agenten, zwei Token, ein vollstaendiger Dialog.

Prueft, was die Unit-Tests nicht koennen: dass Identitaet wirklich aus dem
Bearer-Token kommt, dass ein fremdes Token abgewiesen wird, und dass die
Regelverstoesse als Werkzeugfehler beim Agenten ankommen.
"""

import json
import socket
import threading
import time

import pytest
import uvicorn
from mcp_helpers import valid_post, valid_residual

from dialog_mcp.app import build_app
from dialog_mcp.auth import Config, ParticipantConfig

httpx2 = pytest.importorskip("httpx2")

TOKENS = {"claude": "e2e-claude", "ag": "e2e-ag", "sts": "e2e-owner"}


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def live(tmp_path_factory):
    export = tmp_path_factory.mktemp("export")
    config = Config(
        host="127.0.0.1", port=free_port(),
        database=str(tmp_path_factory.mktemp("db") / "d.sqlite3"),
        export_dir=str(export), public_url="http://127.0.0.1",
        participants=[
            ParticipantConfig("claude", "Claude Code", "debater", TOKENS["claude"]),
            ParticipantConfig("ag", "Antigravity", "debater", TOKENS["ag"]),
            ParticipantConfig("sts", "Steffen", "owner", TOKENS["sts"], human=True),
        ],
    )
    app = build_app(config)
    server = uvicorn.Server(uvicorn.Config(app, host=config.host, port=config.port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.1)
    assert server.started, "Server ist nicht gestartet"
    yield f"http://{config.host}:{config.port}/mcp", export
    server.should_exit = True
    thread.join(timeout=5)


class ToolFailed(RuntimeError):
    """Werkzeugfehler des Servers, so wie ihn ein Agent zu sehen bekommt."""


async def call(url: str, token: str, tool: str, args: dict):
    from mcp.client import Client
    from mcp.client.streamable_http import streamable_http_client

    error: str | None = None
    payload = None
    # Der Fehler wird erst ausserhalb der Task-Group geworfen - sonst verpackt
    # anyio ihn in eine ExceptionGroup und `pytest.raises(match=...)` greift nicht.
    async with httpx2.AsyncClient(headers={"Authorization": f"Bearer {token}"}) as http:
        async with Client(streamable_http_client(url, http_client=http)) as client:
            result = await client.call_tool(tool, args)
            if result.is_error:
                error = result.content[0].text
            elif result.structured_content is not None:
                payload = result.structured_content
            else:
                payload = json.loads(result.content[0].text)
    if error is not None:
        raise ToolFailed(error)
    return payload


@pytest.mark.anyio
async def test_unknown_token_cannot_reach_any_tool(live):
    url, _ = live
    with pytest.raises(Exception):
        await call(url, "kein-gueltiges-token", "dialog_list", {})


@pytest.mark.anyio
async def test_full_dialogue_over_http(live):
    url, export = live
    await call(url, TOKENS["sts"], "dialog_open", {
        "slug": "e2e", "topic": "Allowlist statt Denylist", "debaters": ["claude", "ag"], "max_rounds": 2,
    })

    # Sondenphase: blind, und verdeckt bis alle vorliegen.
    await call(url, TOKENS["claude"], "dialog_probe_submit", {
        "slug": "e2e", "artifact": "export.ps1:44 — Denylist laesst .pem durch",
        "evidence": [{"path": "scripts/export-aos.ps1", "locator": "Zeile 44"}],
    })
    with pytest.raises(ToolFailed, match="verdeckt"):
        await call(url, TOKENS["ag"], "dialog_probe_results", {"slug": "e2e"})

    await call(url, TOKENS["ag"], "dialog_probe_submit", {
        "slug": "e2e", "artifact": "install.ps1:12 — Hardlink driftet",
        "evidence": [{"path": "install.ps1", "locator": "Zeile 12"}],
    })
    results = await call(url, TOKENS["ag"], "dialog_probe_results", {"slug": "e2e"})
    assert results["convergence_possible"] is False

    status = await call(url, TOKENS["claude"], "dialog_probe_resolve", {
        "slug": "e2e", "outcome": "diverged", "rationale": "Zwei verschiedene Stellen benannt.",
    })
    assert status["state"] == "debating" and status["turn"] == "claude"

    # Identitaet kommt aus dem Token: ag kann nicht in Claudes Zug schreiben.
    with pytest.raises(ToolFailed, match="ist am Zug"):
        await call(url, TOKENS["ag"], "dialog_post", {"slug": "e2e", **valid_post()})

    # Regelverstoss kommt als Werkzeugfehler beim Agenten an.
    broken = valid_post()
    broken["objections"] = [{"claim": "schlecht", "reasoning": "weil", "retract_if": ""}]
    with pytest.raises(ToolFailed, match=r"retract_if"):
        await call(url, TOKENS["claude"], "dialog_post", {"slug": "e2e", **broken})

    await call(url, TOKENS["claude"], "dialog_post", {"slug": "e2e", **valid_post()})
    await call(url, TOKENS["ag"], "dialog_post", {"slug": "e2e", **valid_post()})

    # Letzte Runde: ohne Restdifferenz kein Abschluss.
    with pytest.raises(ToolFailed, match="Restdifferenz"):
        await call(url, TOKENS["claude"], "dialog_post", {"slug": "e2e", **valid_post()})

    for token in (TOKENS["claude"], TOKENS["ag"]):
        await call(url, token, "dialog_post", {"slug": "e2e", **valid_post(residual=valid_residual())})

    final = await call(url, TOKENS["claude"], "dialog_close", {
        "slug": "e2e", "summary": "Allowlist beschlossen, Restdifferenz benannt.",
    })
    assert final["state"] == "done"

    written = {p.name for p in (export / "e2e").iterdir()}
    assert {"status.md", "probes.md", "from-claude.md", "from-ag.md", "outcome.md"} <= written


@pytest.mark.anyio
async def test_converged_probes_end_the_thread_without_debate(live):
    url, export = live
    await call(url, TOKENS["sts"], "dialog_open", {
        "slug": "e2e-konvergent", "topic": "Offensichtlicher Fall", "debaters": ["claude", "ag"],
    })
    await call(url, TOKENS["claude"], "dialog_probe_submit", {
        "slug": "e2e-konvergent", "artifact": "install.ps1:12 — Hardlink driftet",
        "evidence": [{"path": "install.ps1", "locator": "Zeile 12"}],
    })
    await call(url, TOKENS["ag"], "dialog_probe_submit", {
        "slug": "e2e-konvergent", "artifact": "install.ps1:12 — Hardlink driftet",
        "evidence": [{"path": "install.ps1", "locator": "Zeile 12"},
                     {"path": "docs/AOS-Loop-Dokumentation.md", "locator": "Zeile 79"}],
    })
    status = await call(url, TOKENS["ag"], "dialog_probe_resolve", {
        "slug": "e2e-konvergent", "outcome": "converged",
        "rationale": "Gleiches Artefakt, unabhaengiger Evidenzkontakt.",
    })
    assert status["state"] == "done" and status["outcome"] == "converged"
    assert (export / "e2e-konvergent" / "probes.md").exists()
    # Keine Debatte gefuehrt.
    assert not (export / "e2e-konvergent" / "from-claude.md").exists()


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"
