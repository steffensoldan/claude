"""Ein Dialog = eine HTML-Datei.

Der Zustand steht als JSON-Block in der Datei, die zugleich Liveticker und
Abschlussdokument ist. Gelesen wird der Block, geschrieben wird die ganze Datei
neu - atomar ueber `os.replace`, damit nie ein halber Stand auf der Platte liegt.

Waehrend der Sondenphase liegen die Artefakte bewusst *nicht* in dieser Datei,
sondern je Teilnehmer in `<slug>.probe-<id>.json`. So enthaelt der Ticker sie
nicht, solange die Phase laeuft - auch nicht fuer den mitlesenden Menschen.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")

DATA_OPEN = '<script type="application/json" id="dialog-data">'
DATA_CLOSE = "</script>"


class DialogError(Exception):
    """Ablauf- oder Regelverstoss. Die Meldung geht woertlich an den Agenten."""


def now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def encode_data(data: dict[str, Any]) -> str:
    """JSON fuer einen <script>-Block.

    `<` wird als \\u003c geschrieben - damit kann kein Beitragstext den Block
    schliessen (`</script>`) und die Datei bleibt trotzdem gueltiges JSON.
    """
    return json.dumps(data, ensure_ascii=False, indent=1).replace("<", "\\u003c")


def decode_data(html: str) -> dict[str, Any]:
    start = html.find(DATA_OPEN)
    if start < 0:
        raise DialogError("Kein Datenblock in der Datei - ist das eine dialog-lite-Datei?")
    start += len(DATA_OPEN)
    end = html.find(DATA_CLOSE, start)
    if end < 0:
        raise DialogError("Datenblock ist nicht geschlossen - Datei beschaedigt.")
    return json.loads(html[start:end])


# -- Dateien ------------------------------------------------------------


def thread_path(directory: str | Path, slug: str) -> Path:
    return Path(directory) / f"{slug}.html"


def probe_path(directory: str | Path, slug: str, who: str) -> Path:
    return Path(directory) / f"{slug}.probe-{who}.json"


def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=path.suffix)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def load(directory: str | Path, slug: str) -> dict[str, Any]:
    path = thread_path(directory, slug)
    if not path.exists():
        raise DialogError(f"Thread {slug!r} gibt es nicht in {directory}.")
    return decode_data(path.read_text(encoding="utf-8"))


def save(directory: str | Path, data: dict[str, Any], expect_revision: int) -> dict[str, Any]:
    """Schreibt den Thread, wenn seit dem Lesen niemand dazwischengeschrieben hat.

    Zwei Prozesse teilen sich hier eine Datei. Der Zugwechsel verhindert das
    normalerweise; der Zaehler faengt den Rest ab, statt stillschweigend zu
    ueberschreiben.
    """
    from .render import render

    path = thread_path(directory, data["slug"])
    if path.exists():
        current = decode_data(path.read_text(encoding="utf-8")).get("revision", 0)
        if current != expect_revision:
            raise DialogError(
                f"Gleichzeitige Aenderung an {data['slug']!r} (Stand {current}, erwartet "
                f"{expect_revision}). Lies den Thread neu und versuch es noch einmal."
            )
    data["revision"] = expect_revision + 1
    data["updated"] = now()
    write_atomic(path, render(data))
    return data


def list_threads(directory: str | Path) -> list[dict[str, Any]]:
    out = []
    for path in sorted(Path(directory).glob("*.html")):
        try:
            out.append(summary(decode_data(path.read_text(encoding="utf-8"))))
        except (DialogError, json.JSONDecodeError):
            continue  # fremde HTML-Datei im Ordner - nicht unser Problem
    return out


def summary(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "slug": data["slug"],
        "topic": data["topic"],
        "state": data["state"],
        "round": data["round"],
        "max_rounds": data["max_rounds"],
        "turn": data["turn"],
        "participants": data["participants"],
    }


# -- Uebergaenge --------------------------------------------------------


def open_thread(
    directory: str | Path, *, me: str, slug: str, topic: str, partner: str, max_rounds: int = 3
) -> dict[str, Any]:
    if not SLUG_RE.match(slug or ""):
        raise DialogError("slug: Kleinbuchstaben, Ziffern und Bindestriche, hoechstens 64 Zeichen.")
    if not ID_RE.match(partner or ""):
        raise DialogError("partner: Buchstaben, Ziffern, Punkt, Bindestrich, Unterstrich.")
    if partner == me:
        raise DialogError("Ein Dialog braucht zwei verschiedene Teilnehmer.")
    if max_rounds < 1:
        raise DialogError("max_rounds muss mindestens 1 sein.")
    if thread_path(directory, slug).exists():
        raise DialogError(f"Thread {slug!r} gibt es schon.")

    data = {
        "slug": slug,
        "topic": topic,
        "participants": [me, partner],
        "state": "probing",
        "turn": None,
        "round": 1,
        "max_rounds": max_rounds,
        "revision": 0,
        "created": now(),
        "updated": now(),
        "probes": [],
        "probes_pending": [me, partner],
        "probe_outcome": None,
        "posts": [],
        "result": None,
    }
    return save(directory, data, expect_revision=0)


def _require_participant(data: dict[str, Any], me: str) -> None:
    if me not in data["participants"]:
        raise DialogError(f"{me!r} nimmt an {data['slug']!r} nicht teil.")


def _require_open(data: dict[str, Any]) -> None:
    if data["state"] == "done":
        raise DialogError(
            f"Thread {data['slug']!r} ist abgeschlossen und damit terminal. "
            "Fuer neuen Klaerungsbedarf einen neuen Thread anlegen."
        )


def submit_probe(directory: str | Path, *, me: str, slug: str, artifact: str) -> dict[str, Any]:
    data = load(directory, slug)
    _require_participant(data, me)
    _require_open(data)
    if data["state"] != "probing":
        raise DialogError(f"Die Sondenphase von {slug!r} ist vorbei (Zustand: {data['state']}).")
    if not (artifact or "").strip():
        raise DialogError("Die Sonde braucht ein Artefakt: Datei und Zeile, Testfall, Entscheidung, Zahl.")

    path = probe_path(directory, slug, me)
    if path.exists():
        raise DialogError("Deine Sonde liegt bereits vor.")
    write_atomic(path, json.dumps({"who": me, "artifact": artifact.strip(), "at": now()}, ensure_ascii=False))

    pending = [p for p in data["participants"] if not probe_path(directory, slug, p).exists()]
    data["probes_pending"] = pending
    if not pending:
        data["state"] = "probe_review"
    return save(directory, data, data["revision"])


def resolve_probes(
    directory: str | Path, *, me: str, slug: str, outcome: str, rationale: str
) -> dict[str, Any]:
    data = load(directory, slug)
    _require_participant(data, me)
    _require_open(data)
    if data["state"] != "probe_review":
        raise DialogError(
            f"Die Sonden von {slug!r} sind noch nicht vollstaendig "
            f"(es fehlen: {', '.join(data['probes_pending']) or 'keine'})."
        )
    if outcome not in ("converged", "diverged"):
        raise DialogError("outcome: 'converged' oder 'diverged'.")
    if not (rationale or "").strip():
        raise DialogError("Die Bewertung der Sondenphase braucht eine Begruendung.")

    probes = []
    for who in data["participants"]:
        path = probe_path(directory, slug, who)
        probes.append(json.loads(path.read_text(encoding="utf-8")))
    data["probes"] = probes
    data["probe_outcome"] = {"outcome": outcome, "rationale": rationale.strip(), "by": me, "at": now()}

    if outcome == "converged":
        data["state"] = "done"
        data["turn"] = None
        data["result"] = {
            "summary": f"Sonden stimmten ueberein, keine Debatte noetig. {rationale.strip()}",
            "by": me,
            "at": now(),
        }
    else:
        data["state"] = "debating"
        data["turn"] = data["participants"][0]

    saved = save(directory, data, data["revision"])
    for who in data["participants"]:  # Sonden sind jetzt im Thread - Beiwerk aufraeumen
        probe_path(directory, slug, who).unlink(missing_ok=True)
    return saved


def post(
    directory: str | Path, *, me: str, slug: str, body: str, objections: list[dict[str, str]] | None = None
) -> dict[str, Any]:
    data = load(directory, slug)
    _require_participant(data, me)
    _require_open(data)
    if data["state"] != "debating":
        raise DialogError(
            f"In {slug!r} laeuft keine Debatte (Zustand: {data['state']}). "
            "Die Sondenphase muss erst als divergent bewertet werden."
        )
    if data["turn"] is None:
        raise DialogError("Die letzte Runde ist gesprochen - der Thread wartet auf den Abschluss.")
    if data["turn"] != me:
        raise DialogError(f"{data['turn']!r} ist am Zug, nicht {me!r}.")
    if not (body or "").strip():
        raise DialogError("Der Beitrag ist leer.")

    cleaned = []
    for item in objections or []:
        claim = str(item.get("claim", "")).strip()
        retract_if = str(item.get("retract_if", "")).strip()
        if not claim:
            raise DialogError("Ein Einwand braucht eine Aussage (claim).")
        if not retract_if:
            raise DialogError(
                f"Der Einwand {claim!r} hat keine Ruecknahmebedingung. Jeder Einwand endet mit "
                "'Ich ziehe das zurueck, wenn ___'. Wer das nicht angeben kann, hat ein Stilmittel "
                "geliefert, keinen Einwand."
            )
        cleaned.append({"claim": claim, "retract_if": retract_if})

    round_no = int(data["round"])
    data["posts"].append(
        {"who": me, "round": round_no, "body": body.strip(), "objections": cleaned, "at": now()}
    )

    other = [p for p in data["participants"] if p != me][0]
    spoken = {p["who"] for p in data["posts"] if p["round"] == round_no}
    if set(data["participants"]) <= spoken:
        # Wie im AOS: der zweite Sprecher einer Runde erhoeht den Zaehler.
        if round_no >= int(data["max_rounds"]):
            data["turn"] = None
        else:
            data["round"] = round_no + 1
            data["turn"] = other
    else:
        data["turn"] = other
    return save(directory, data, data["revision"])


def close(directory: str | Path, *, me: str, slug: str, summary_text: str) -> dict[str, Any]:
    data = load(directory, slug)
    _require_participant(data, me)
    _require_open(data)
    if not (summary_text or "").strip():
        raise DialogError("Der Abschluss braucht ein Ergebnis in eigenen Worten.")
    data["state"] = "done"
    data["turn"] = None
    data["result"] = {"summary": summary_text.strip(), "by": me, "at": now()}
    return save(directory, data, data["revision"])


def read(directory: str | Path, *, me: str, slug: str) -> dict[str, Any]:
    """Voller Verlauf - fremde Sonden bleiben verdeckt, solange die Phase laeuft."""
    data = load(directory, slug)
    _require_participant(data, me)
    view = dict(data)
    if data["state"] in ("probing", "probe_review"):
        view["probes"] = None
        view["probes_note"] = (
            "Verdeckt, bis die Sondenphase aufgeloest ist. "
            f"Eingegangen von: {', '.join(p for p in data['participants'] if p not in data['probes_pending']) or 'niemandem'}."
        )
    return view
