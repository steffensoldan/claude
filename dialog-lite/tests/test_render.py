from lite_helpers import A, B, obj

from dialog_lite import thread


def html_of(d, slug="t") -> str:
    return thread.thread_path(d, slug).read_text(encoding="utf-8")


def test_ticker_reloads_while_running_and_stops_when_done(debating):
    assert 'http-equiv="refresh"' in html_of(debating)
    thread.close(debating, me=A, slug="t", summary_text="Fertig.")
    done = html_of(debating)
    assert 'http-equiv="refresh"' not in done
    assert "lädt sich nicht mehr neu" in done


def test_new_entries_show_up_in_the_file(debating):
    before = html_of(debating)
    assert "Ein ganz bestimmter Satz." not in before
    thread.post(debating, me=A, slug="t", body="Ein ganz bestimmter Satz.", objections=obj())
    after = html_of(debating)
    assert "Ein ganz bestimmter Satz." in after
    assert "Ich ziehe das zurück, wenn: ein Hash-Vergleich Gleichheit zeigt" in after


def test_probe_phase_shows_who_is_missing_not_what_they_wrote(d):
    thread.open_thread(d, me=A, slug="t", topic="Thema", partner=B)
    thread.submit_probe(d, me=A, slug="t", artifact="GEHEIM-a:1")
    page = html_of(d)
    assert "GEHEIM" not in page
    assert "verdeckt" in page
    assert "Es fehlt: beta" in page


def test_result_is_part_of_the_document(debating):
    thread.close(debating, me=B, slug="t", summary_text="Allowlist beschlossen.")
    page = html_of(debating)
    assert "Ergebnis" in page and "Allowlist beschlossen." in page
    assert "beta" in page


def test_body_text_cannot_inject_markup(debating):
    thread.post(debating, me=A, slug="t", body="<img src=x onerror=alert(1)>")
    page = html_of(debating)
    assert "<img src=x" not in page
    assert "&lt;img src=x" in page
