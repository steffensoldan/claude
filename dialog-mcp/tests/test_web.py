import re

import pytest
from conftest import valid_post
from starlette.testclient import TestClient

from dialog_mcp.app import build_app
from dialog_mcp.auth import Config, ParticipantConfig

TOKENS = {"claude": "tok-claude", "ag": "tok-ag", "sts": "tok-owner"}


@pytest.fixture
def app(tmp_path):
    config = Config(
        host="127.0.0.1", port=0, database=":memory:",
        export_dir=str(tmp_path / "dialog"), public_url="http://testserver",
        participants=[
            ParticipantConfig("claude", "Claude Code", "debater", TOKENS["claude"]),
            ParticipantConfig("ag", "Antigravity", "debater", TOKENS["ag"]),
            ParticipantConfig("sts", "Steffen", "owner", TOKENS["sts"], human=True),
        ],
    )
    return build_app(config)


def login(client: TestClient, who: str) -> str:
    client.post("/login", data={"token": TOKENS[who]})
    page = client.get("/")
    match = re.search(r'name="csrf" value="([^"]+)"', page.text)
    return match.group(1) if match else ""


def csrf_for(client: TestClient, slug: str) -> str:
    page = client.get(f"/t/{slug}")
    match = re.search(r'name="csrf" value="([^"]+)"', page.text)
    return match.group(1) if match else ""


def test_login_rejects_unknown_token(app):
    with TestClient(app) as client:
        response = client.post("/login", data={"token": "falsch"})
        assert response.status_code == 401
        assert "nicht erkannt" in response.text.lower()


def test_index_requires_login(app):
    with TestClient(app) as client:
        assert client.get("/").url.path == "/login"


def test_other_probes_are_not_served_during_the_blind_phase(app):
    service = app.state.service
    service.open_thread("sts", slug="t", topic="Blindtest", debaters=["claude", "ag"])
    service.submit_probe("claude", "t", "GEHEIMES-ARTEFAKT-VON-CLAUDE", [{"path": "a", "locator": "1"}])

    with TestClient(app) as client:
        login(client, "ag")
        page = client.get("/t/t")
        assert page.status_code == 200
        # Blindheit heisst: der Server liefert es gar nicht erst aus.
        assert "GEHEIMES-ARTEFAKT-VON-CLAUDE" not in page.text
        assert "Verdeckt" in page.text or "Es fehlen" in page.text


def test_probe_can_be_submitted_from_the_browser(app):
    service = app.state.service
    service.open_thread("sts", slug="t", topic="Blindtest", debaters=["claude", "ag"], probers=["sts"])

    with TestClient(app) as client:
        login(client, "sts")
        token = csrf_for(client, "t")
        client.post("/t/t/probe", data={
            "csrf": token,
            "artifact": "src/app.py:120 — falsche Abbruchbedingung",
            "evidence": "src/app.py — Zeile 120–134\ntests/test_app.py — Zeile 12",
        })
    probes = service.store.probes("t", 1)
    assert [p["participant"] for p in probes] == ["sts"]
    assert probes[0]["is_human"] is True
    assert probes[0]["evidence"] == [
        {"path": "src/app.py", "locator": "Zeile 120–134"},
        {"path": "tests/test_app.py", "locator": "Zeile 12"},
    ]


def test_form_without_csrf_token_is_refused(app):
    app.state.service.open_thread("sts", slug="t", topic="X", debaters=["claude", "ag"])
    with TestClient(app) as client:
        login(client, "claude")
        response = client.post("/t/t/probe", data={"artifact": "x", "evidence": "a — 1"})
        assert response.status_code == 403
        assert "CSRF" in response.text
    assert app.state.service.store.probes("t", 1) == []


def test_control_routes_are_owner_only(app):
    service = app.state.service
    service.open_thread("sts", slug="t", topic="X", debaters=["claude", "ag"])
    with TestClient(app) as client:
        login(client, "claude")
        token = csrf_for(client, "t")
        for route in ("extend", "repeat-probes", "close"):
            response = client.post(
                f"/t/t/{route}",
                data={"csrf": token, "extra_rounds": 1, "reason": "weil", "summary": "weil"},
            )
            assert response.status_code == 403, route
            assert "Eigentuemer" in response.text
    assert service.status("t")["max_rounds"] == 3


def test_owner_can_extend_from_the_browser(app):
    service = app.state.service
    service.open_thread("sts", slug="t", topic="X", debaters=["claude", "ag"])
    service.submit_probe("claude", "t", "a:1", [{"path": "a", "locator": "1"}])
    service.submit_probe("ag", "t", "b:2", [{"path": "b", "locator": "2"}])
    service.resolve_probes("sts", "t", "diverged", "verschieden")

    with TestClient(app) as client:
        login(client, "sts")
        token = csrf_for(client, "t")
        client.post("/t/t/extend", data={"csrf": token, "extra_rounds": 2, "reason": "Punkt drei offen"})
    assert service.status("t")["max_rounds"] == 5


def test_thread_page_shows_the_debate_record(app):
    service = app.state.service
    service.open_thread("sts", slug="t", topic="X", debaters=["claude", "ag"])
    service.submit_probe("claude", "t", "a:1", [{"path": "a", "locator": "1"}])
    service.submit_probe("ag", "t", "b:2", [{"path": "b", "locator": "2"}])
    service.resolve_probes("sts", "t", "diverged", "verschieden")
    service.post("claude", "t", valid_post())

    with TestClient(app) as client:
        login(client, "ag")
        page = client.get("/t/t").text
    assert "Ein Beitrag mit Substanz." in page
    assert "Ich ziehe das zurück, wenn" in page
    assert "geopfert wird" in page


def test_event_stream_requires_login(app):
    with TestClient(app) as client:
        assert client.get("/events/t").status_code == 403
