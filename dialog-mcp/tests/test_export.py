import re

from conftest import valid_post, valid_residual


def run_full_thread(service) -> str:
    service.open_thread("sts", slug="aos-test", topic="Testdialog", debaters=["claude", "ag"], max_rounds=2)
    service.submit_probe("claude", "aos-test", "src/a.py:12", [{"path": "src/a.py", "locator": "Zeile 12"}])
    service.submit_probe("ag", "aos-test", "src/b.py:40", [{"path": "src/b.py", "locator": "Zeile 40"}])
    service.resolve_probes("claude", "aos-test", "diverged", "Verschiedene Stellen.")
    service.post("claude", "aos-test", valid_post())
    service.post("ag", "aos-test", valid_post())
    service.post("claude", "aos-test", valid_post(residual=valid_residual()))
    service.post("ag", "aos-test", valid_post(residual=valid_residual()))
    result = service.close("sts", "aos-test", "Zwei Nachbesserungen vereinbart.")
    return result["export"]


def test_export_matches_the_aos_layout(service, tmp_path):
    target = run_full_thread(service)
    files = {p.name for p in (tmp_path / "dialog" / "aos-test").iterdir()}
    assert {"status.md", "probes.md", "from-claude.md", "from-ag.md", "outcome.md"} <= files
    assert target.endswith("aos-test")


def test_status_md_uses_the_aos_keys(service, tmp_path):
    run_full_thread(service)
    status = (tmp_path / "dialog" / "aos-test" / "status.md").read_text(encoding="utf-8")
    keys = [line.split(":")[0] for line in status.strip().splitlines()]
    assert keys == ["status", "max_rounds", "current_round", "started", "topic"]
    assert status.startswith("status: done")
    assert re.search(r"^started: \d{4}-\d{2}-\d{2}$", status, re.M)


def test_post_headers_and_signature_match_the_aos_convention(service, tmp_path):
    run_full_thread(service)
    text = (tmp_path / "dialog" / "aos-test" / "from-claude.md").read_text(encoding="utf-8")
    # Vorbild: **[2026-06-30 10:30, Claude Code — Runde 1]**  ...  — Claude Code
    assert re.search(r"^\*\*\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}, Claude Code — Runde 1\]\*\*$", text, re.M)
    assert re.search(r"^— Claude Code$", text, re.M)
    assert text.count("— Claude Code\n") == 2  # zwei Beitraege, zwei Signaturen


def test_export_carries_the_debate_rules_into_markdown(service, tmp_path):
    run_full_thread(service)
    text = (tmp_path / "dialog" / "aos-test" / "from-ag.md").read_text(encoding="utf-8")
    assert "Ich ziehe das zurück, wenn" in text
    assert "**Priorisierung**" in text and "geopfert wird" in text
    assert "| Dimension | Bewertung | Anmerkung |" in text
    assert "**Ungelöste Restdifferenz**" in text


def test_files_are_utf8_without_bom_and_lf(service, tmp_path):
    run_full_thread(service)
    for path in (tmp_path / "dialog" / "aos-test").iterdir():
        raw = path.read_bytes()
        assert not raw.startswith(b"\xef\xbb\xbf"), f"{path.name} traegt ein BOM"
        assert b"\r\n" not in raw, f"{path.name} enthaelt CRLF"
        raw.decode("utf-8")


def test_probes_are_exported_with_human_marker(service, tmp_path):
    service.open_thread("sts", slug="p", topic="X", debaters=["claude", "ag"], probers=["sts"])
    for who, artifact in (("claude", "a:1"), ("ag", "b:2"), ("sts", "c:3")):
        service.submit_probe(who, "p", artifact, [{"path": who, "locator": "1"}])
    service.resolve_probes("claude", "p", "diverged", "drei verschiedene Befunde")
    service.close("sts", "p", "abgebrochen")
    probes = (tmp_path / "dialog" / "p" / "probes.md").read_text(encoding="utf-8")
    assert "## Steffen *(Mensch)* — Sondenrunde 1" in probes
    assert "## Claude Code — Sondenrunde 1" in probes
