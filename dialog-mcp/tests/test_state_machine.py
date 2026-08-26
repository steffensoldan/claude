import pytest
from mcp_helpers import valid_post, valid_residual

from dialog_mcp.rules import RuleViolation
from dialog_mcp.service import DialogError


def test_probes_stay_hidden_until_all_are_in(service):
    service.open_thread("sts", slug="t", topic="X", debaters=["claude", "ag"])
    service.submit_probe("claude", "t", "src/a.py:12", [{"path": "src/a.py", "locator": "12"}])
    with pytest.raises(DialogError) as exc:
        service.probe_results("ag", "t")
    assert "verdeckt" in str(exc.value)
    assert "ag" in str(exc.value)
    assert service.read("ag", "t")["probes"] is None


def test_probes_become_visible_once_complete(service):
    service.open_thread("sts", slug="t", topic="X", debaters=["claude", "ag"])
    service.submit_probe("claude", "t", "src/a.py:12", [{"path": "src/a.py", "locator": "12"}])
    service.submit_probe("ag", "t", "src/a.py:12", [{"path": "tests/t.py", "locator": "3"}])
    assert service.status("t")["state"] == "probe_review"
    results = service.probe_results("ag", "t")
    assert results["convergence_possible"] is True
    assert len(results["probes"]) == 2


def test_convergence_closes_the_thread_without_debate(service):
    service.open_thread("sts", slug="t", topic="X", debaters=["claude", "ag"])
    service.submit_probe("claude", "t", "src/a.py:12", [{"path": "src/a.py", "locator": "12"}])
    service.submit_probe("ag", "t", "src/a.py:12", [{"path": "tests/t.py", "locator": "3"}])
    status = service.resolve_probes("claude", "t", "converged", "Gleiches Artefakt, unabhaengige Evidenz.")
    assert status["state"] == "done"
    assert status["outcome"] == "converged"


def test_convergence_refused_without_evidence(service):
    service.open_thread("sts", slug="t", topic="X", debaters=["claude", "ag"], profile="light")
    service.submit_probe("claude", "t", "src/a.py:12")
    service.submit_probe("ag", "t", "src/a.py:12")
    with pytest.raises(DialogError) as exc:
        service.resolve_probes("claude", "t", "converged", "sieht gleich aus")
    assert "geteilter Prior" in str(exc.value)


def test_repeat_starts_a_fresh_blind_round(service):
    service.open_thread("sts", slug="t", topic="X", debaters=["claude", "ag"], profile="light")
    service.submit_probe("claude", "t", "a")
    service.submit_probe("ag", "t", "a")
    status = service.resolve_probes("sts", "t", "repeat", "Ohne Evidenz wertlos.")
    assert status["state"] == "probing" and status["probe_round"] == 2
    service.submit_probe("claude", "t", "b")  # gleiche Runde erneut moeglich
    assert service.status("t")["probes_missing"] == ["ag"]


def test_probers_include_humans_and_extra_agents(service):
    service.open_thread("sts", slug="t", topic="X", debaters=["claude", "ag"], probers=["sts", "gast"])
    assert set(service.status("t")["probers"]) == {"sts", "gast", "claude", "ag"}


def test_cannot_post_before_probes_resolved(service):
    service.open_thread("sts", slug="t", topic="X", debaters=["claude", "ag"])
    with pytest.raises(DialogError) as exc:
        service.post("claude", "t", valid_post())
    assert "keine Debatte" in str(exc.value)


def test_out_of_turn_post_is_rejected(debating):
    with pytest.raises(DialogError) as exc:
        debating.post("ag", "t", valid_post())
    assert "'claude' ist am Zug" in str(exc.value)


def test_round_advances_only_after_the_second_speaker(debating):
    debating.post("claude", "t", valid_post())
    after_first = debating.status("t")
    assert after_first["round"] == 1 and after_first["turn"] == "ag"
    debating.post("ag", "t", valid_post())
    status = debating.status("t")
    assert status["round"] == 2 and status["turn"] == "claude"


def test_final_round_needs_residual_and_then_nobody_is_on_turn(debating):
    for _ in range(2):  # Runden 1 und 2
        debating.post("claude", "t", valid_post())
        debating.post("ag", "t", valid_post())
    assert debating.status("t")["round"] == 3

    # In Runde 3 ist kein Einwand mehr Pflicht - die Restdifferenz aber sehr wohl.
    with pytest.raises(RuleViolation) as exc:
        debating.post("claude", "t", valid_post(objections=[]))
    assert exc.value.field == "residual"

    debating.post("claude", "t", valid_post(residual=valid_residual()))
    debating.post("ag", "t", valid_post(residual=valid_residual()))
    status = debating.status("t")
    assert status["turn"] is None and status["state"] == "debating"


def test_debater_cannot_close_mid_debate_but_owner_can(debating):
    with pytest.raises(DialogError) as exc:
        debating.close("claude", "t", "abgebrochen")
    assert "Vorzeitig schliesst nur der Eigentuemer" in str(exc.value)
    assert debating.close("sts", "t", "Abbruch aus Zeitgruenden")["state"] == "done"


def test_done_thread_is_terminal(debating):
    debating.close("sts", "t", "fertig")
    with pytest.raises(DialogError) as exc:
        debating.post("claude", "t", valid_post())
    assert "terminal" in str(exc.value)
    with pytest.raises(DialogError):
        debating.submit_probe("claude", "t", "x", [{"path": "a", "locator": "1"}])


def test_only_owner_extends(debating):
    with pytest.raises(DialogError) as exc:
        debating.extend("claude", "t", 1, "brauche mehr Runden")
    assert "Advisory" in str(exc.value)
    assert debating.extend("sts", "t", 2, "Punkt drei offen")["max_rounds"] == 5


def test_extension_after_final_round_reopens_the_turn(debating):
    for _ in range(2):
        debating.post("claude", "t", valid_post())
        debating.post("ag", "t", valid_post())
    debating.post("claude", "t", valid_post(residual=valid_residual()))
    debating.post("ag", "t", valid_post(residual=valid_residual()))
    assert debating.status("t")["turn"] is None

    status = debating.extend("sts", "t", 1, "Allowlist-Frage offen")
    assert status["round"] == 4 and status["turn"] == "claude" and status["max_rounds"] == 4


def test_agents_recommend_extension_without_deciding(debating):
    debating.post("claude", "t", valid_post(extension="Verlaengerung um 1 Runde empfohlen."))
    kinds = [e["kind"] for e in debating.store.events_since("t", 0)]
    assert "extension_recommended" in kinds
    assert debating.status("t")["max_rounds"] == 3


def test_open_rejects_bad_input(service):
    with pytest.raises(DialogError):
        service.open_thread("sts", slug="Nicht Gueltig", topic="X", debaters=["claude", "ag"])
    with pytest.raises(DialogError):
        service.open_thread("sts", slug="t", topic="X", debaters=["claude", "claude"])
    with pytest.raises(DialogError):
        service.open_thread("sts", slug="t", topic="X", debaters=["claude", "unbekannt"])
    service.open_thread("sts", slug="t", topic="X", debaters=["claude", "ag"])
    with pytest.raises(DialogError):
        service.open_thread("sts", slug="t", topic="Y", debaters=["claude", "ag"])
