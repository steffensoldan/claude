import json

import pytest
from lite_helpers import A, B, obj

from dialog_lite import thread
from dialog_lite.thread import DialogError


# -- Datei als Speicher -------------------------------------------------

def test_file_is_its_own_storage(d):
    thread.open_thread(d, me=A, slug="t", topic="Thema", partner=B)
    html = thread.thread_path(d, "t").read_text(encoding="utf-8")
    assert "<!doctype html>" in html
    assert thread.decode_data(html)["topic"] == "Thema"


def test_round_trip_survives_html_and_script_characters(d):
    nasty = 'Ein <div> & ein </script> und "Anführungszeichen" — mit Umlauten: äöüß'
    thread.open_thread(d, me=A, slug="t", topic=nasty, partner=B)
    thread.submit_probe(d, me=A, slug="t", artifact="a:1")
    thread.submit_probe(d, me=B, slug="t", artifact="b:2")
    thread.resolve_probes(d, me=A, slug="t", outcome="diverged", rationale="verschieden")
    thread.post(d, me=A, slug="t", body=nasty, objections=obj(claim=nasty))

    data = thread.load(d, "t")
    assert data["topic"] == nasty
    assert data["posts"][0]["body"] == nasty
    assert data["posts"][0]["objections"][0]["claim"] == nasty
    # Der Datenblock darf durch keinen Beitragstext vorzeitig schliessen.
    html = thread.thread_path(d, "t").read_text(encoding="utf-8")
    assert html.count('id="dialog-data"') == 1
    assert html.index(thread.DATA_CLOSE, html.index(thread.DATA_OPEN)) > html.index("Umlauten")


def test_concurrent_write_is_refused_not_silently_overwritten(d):
    thread.open_thread(d, me=A, slug="t", topic="Thema", partner=B)
    first = thread.load(d, "t")
    second = thread.load(d, "t")
    thread.save(d, first, first["revision"])
    with pytest.raises(DialogError, match="Gleichzeitige Aenderung"):
        thread.save(d, second, second["revision"])


def test_listing_ignores_foreign_html_in_the_folder(d, tmp_path):
    thread.open_thread(d, me=A, slug="t", topic="Thema", partner=B)
    (tmp_path / "fremd.html").write_text("<html>nichts fuer uns</html>", encoding="utf-8")
    assert [t["slug"] for t in thread.list_threads(d)] == ["t"]


# -- Sondenphase --------------------------------------------------------

def test_probe_stays_out_of_the_ticker_file_until_resolved(d):
    thread.open_thread(d, me=A, slug="t", topic="Thema", partner=B)
    thread.submit_probe(d, me=A, slug="t", artifact="GEHEIM-src/a.py:12")

    html = thread.thread_path(d, "t").read_text(encoding="utf-8")
    assert "GEHEIM" not in html
    assert thread.probe_path(d, "t", A).exists()

    view = thread.read(d, me=B, slug="t")
    assert view["probes"] is None
    assert "alpha" in view["probes_note"]
    assert "GEHEIM" not in json.dumps(view, ensure_ascii=False)


def test_probes_appear_once_the_phase_is_resolved(d):
    thread.open_thread(d, me=A, slug="t", topic="Thema", partner=B)
    thread.submit_probe(d, me=A, slug="t", artifact="src/a.py:12")
    assert thread.load(d, "t")["state"] == "probing"
    thread.submit_probe(d, me=B, slug="t", artifact="src/b.py:40")
    assert thread.load(d, "t")["state"] == "probe_review"

    thread.resolve_probes(d, me=B, slug="t", outcome="diverged", rationale="verschieden")
    data = thread.load(d, "t")
    assert [p["who"] for p in data["probes"]] == [A, B]
    assert data["state"] == "debating" and data["turn"] == A
    # Beiwerk aufgeraeumt.
    assert not thread.probe_path(d, "t", A).exists()


def test_converged_probes_end_the_dialogue_without_debate(d):
    thread.open_thread(d, me=A, slug="t", topic="Thema", partner=B)
    thread.submit_probe(d, me=A, slug="t", artifact="src/a.py:12")
    thread.submit_probe(d, me=B, slug="t", artifact="src/a.py:12")
    data = thread.resolve_probes(d, me=A, slug="t", outcome="converged", rationale="Gleiches Artefakt.")
    assert data["state"] == "done" and data["posts"] == []
    assert "keine Debatte" in data["result"]["summary"]


def test_probe_rules(d):
    thread.open_thread(d, me=A, slug="t", topic="Thema", partner=B)
    with pytest.raises(DialogError, match="Artefakt"):
        thread.submit_probe(d, me=A, slug="t", artifact="   ")
    thread.submit_probe(d, me=A, slug="t", artifact="a:1")
    with pytest.raises(DialogError, match="liegt bereits vor"):
        thread.submit_probe(d, me=A, slug="t", artifact="a:2")
    with pytest.raises(DialogError, match="noch nicht vollstaendig"):
        thread.resolve_probes(d, me=A, slug="t", outcome="diverged", rationale="x")
    with pytest.raises(DialogError, match="nimmt an"):
        thread.submit_probe(d, me="fremder", slug="t", artifact="c:3")


# -- Debatte ------------------------------------------------------------

def test_only_the_agent_on_turn_can_write(debating):
    with pytest.raises(DialogError, match="'alpha' ist am Zug"):
        thread.post(debating, me=B, slug="t", body="vorgedraengelt", objections=obj())


def test_objection_without_retract_condition_is_refused(debating):
    with pytest.raises(DialogError, match="Ruecknahmebedingung"):
        thread.post(debating, me=A, slug="t", body="Text",
                    objections=[{"claim": "Das ist schlecht.", "retract_if": ""}])
    assert thread.load(debating, "t")["posts"] == []


def test_empty_post_is_refused(debating):
    with pytest.raises(DialogError, match="leer"):
        thread.post(debating, me=A, slug="t", body="  ")


def test_post_without_objections_is_fine(debating):
    data = thread.post(debating, me=A, slug="t", body="Nur eine Praezisierung.")
    assert data["turn"] == B


def test_round_advances_on_the_second_speaker(debating):
    data = thread.post(debating, me=A, slug="t", body="erster", objections=obj())
    assert data["round"] == 1 and data["turn"] == B
    data = thread.post(debating, me=B, slug="t", body="zweiter", objections=obj())
    assert data["round"] == 2 and data["turn"] == A


def test_after_the_last_round_nobody_is_on_turn(debating):
    for _ in range(3):
        thread.post(debating, me=A, slug="t", body="a")
        thread.post(debating, me=B, slug="t", body="b")
    data = thread.load(debating, "t")
    assert data["round"] == 3 and data["turn"] is None and data["state"] == "debating"
    with pytest.raises(DialogError, match="wartet auf den Abschluss"):
        thread.post(debating, me=A, slug="t", body="noch was")


def test_done_is_terminal(debating):
    thread.close(debating, me=A, slug="t", summary_text="Einig bis auf einen Punkt.")
    for call in (
        lambda: thread.post(debating, me=B, slug="t", body="x"),
        lambda: thread.submit_probe(debating, me=B, slug="t", artifact="x"),
        lambda: thread.close(debating, me=B, slug="t", summary_text="nochmal"),
    ):
        with pytest.raises(DialogError, match="terminal"):
            call()


def test_close_needs_a_result(debating):
    with pytest.raises(DialogError, match="Ergebnis"):
        thread.close(debating, me=A, slug="t", summary_text="  ")


# -- Anlegen ------------------------------------------------------------

def test_open_validates_its_input(d):
    with pytest.raises(DialogError, match="slug"):
        thread.open_thread(d, me=A, slug="Nicht Gueltig", topic="X", partner=B)
    with pytest.raises(DialogError, match="zwei verschiedene"):
        thread.open_thread(d, me=A, slug="t", topic="X", partner=A)
    thread.open_thread(d, me=A, slug="t", topic="X", partner=B)
    with pytest.raises(DialogError, match="gibt es schon"):
        thread.open_thread(d, me=B, slug="t", topic="Y", partner=A)
