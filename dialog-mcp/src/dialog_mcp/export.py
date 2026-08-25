"""Export eines abgeschlossenen Threads im AOS-Markdown-Format.

Zielstruktur ist exakt die des bestehenden AOS-Dialogs, damit ein exportierter
Thread neben `dialog/aos-optimierung/` liegen kann, ohne aufzufallen:

    dialog/<slug>/
      status.md          Steuerungsdatei im AOS-Format
      from-<teilnehmer>.md   je ein Beitragsstrang, angehaengt in Rundenfolge
      probes.md          die Sondenphase (im AOS-Dateimodell nicht vorgesehen)

Alle Dateien werden als UTF-8 **ohne BOM** geschrieben - `dialog/README.md` §4.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .service import Service


def _write(path: Path, text: str) -> None:
    # newline="\n" und encoding="utf-8" (nicht utf-8-sig): kein BOM, keine CRLF.
    path.write_text(text, encoding="utf-8", newline="\n")


def _stamp(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return iso


def _day(iso: str) -> str:
    return _stamp(iso).split(" ")[0]


def render_status(service: "Service", slug: str) -> str:
    t = service.store.thread(slug)
    assert t is not None
    return (
        f"status: {'done' if t['state'] == 'done' else t['state']}\n"
        f"max_rounds: {t['max_rounds']}\n"
        f"current_round: {t['round']}\n"
        f"started: {_day(t['created_at'])}\n"
        f"topic: {t['topic']}\n"
    )


def _evidence_lines(items: list[dict[str, str]]) -> str:
    if not items:
        return ""
    lines = "\n".join(f"- `{e['path']}` — {e['locator']}" for e in items)
    return f"\n**Evidenz**\n\n{lines}\n"


def _objection_lines(items: list[dict[str, str]], heading: str, retract_label: str) -> str:
    if not items:
        return ""
    out = [f"\n**{heading}**\n"]
    for item in items:
        head = item.get("claim") or item.get("field") or ""
        out.append(f"- {head}")
        if item.get("reasoning"):
            out.append(f"  - Begründung: {item['reasoning']}")
        if item.get("retract_if"):
            out.append(f"  - {retract_label}: {item['retract_if']}")
    return "\n".join(out) + "\n"


def _matrix_table(matrix: dict[str, Any] | None) -> str:
    if not matrix:
        return ""
    rows = ["\n**Kriterien-Matrix**\n", "| Dimension | Bewertung | Anmerkung |", "|---|---|---|"]
    for dim, cell in matrix.items():
        note = cell.get("note", "")
        if dim.lower() == "compliance" and cell.get("gate"):
            note = f"Gate: {cell['gate']}. {note}".strip()
        rows.append(f"| {dim.capitalize()} | {cell.get('rating', '')} | {note} |")
    return "\n".join(rows) + "\n"


def render_post(service: "Service", post: dict[str, Any]) -> str:
    who = service.store.participant(post["participant"])
    name = who.display_name if who else post["participant"]
    # Vorbild: Kopfzeile, Leerzeile, Text - wie in dialog/aos-optimierung/.
    parts = [
        f"\n**[{_stamp(post['created_at'])}, {name} — Runde {post['round']}]**\n\n",
        post["body"].rstrip() + "\n",
    ]
    parts.append(_objection_lines(post["objections"], "Einwände", "Ich ziehe das zurück, wenn"))
    parts.append(_objection_lines(post["clearances"], "Entwarnungen", "Diese Entwarnung fällt, wenn"))
    if post.get("priorities"):
        dims = ", ".join(post["priorities"].get("dimensions", []))
        parts.append(
            f"\n**Priorisierung**\n\n{dims} — geopfert wird: {post['priorities'].get('sacrifice', '')}\n"
        )
    parts.append(_matrix_table(post.get("matrix")))
    if post.get("residual"):
        r = post["residual"]
        parts.append(
            "\n**Ungelöste Restdifferenz**\n\n"
            f"1. Differenz: {r.get('difference', '')}\n"
            f"2. Warum nicht durch Argument entscheidbar: {r.get('why_unresolvable', '')}\n"
            f"3. Messung: {r.get('measurement', '')}\n"
        )
    parts.append(_evidence_lines(post["evidence"]))
    if post.get("extension"):
        parts.append(f"\n**Verlängerung empfohlen**\n\n{post['extension']}\n")
    parts.append(f"\n— {name}\n")
    return "".join(parts)


def render_probes(service: "Service", slug: str) -> str:
    probes = service.store.all_probes(slug)
    if not probes:
        return "# Sondenphase\n\nKeine Sonden erfasst.\n"
    out = [
        "# Sondenphase\n\n",
        "Blinde Erstlösungen vor dem ersten Austausch (`debate-mode.md` §0). "
        "Menschliche Sonden sind markiert und zählen im Messdesign nicht als Modellsonde.\n",
    ]
    for probe in probes:
        who = service.store.participant(probe["participant"])
        name = who.display_name if who else probe["participant"]
        tag = " *(Mensch)*" if probe["is_human"] else ""
        out.append(f"\n## {name}{tag} — Sondenrunde {probe['probe_round']}\n")
        out.append(f"\n**Artefakt**\n\n{probe['artifact'].rstrip()}\n")
        out.append(_evidence_lines(probe["evidence"]))
    return "".join(out)


def write_export(service: "Service", slug: str, export_dir: str | Path) -> Path:
    target = Path(export_dir) / slug
    target.mkdir(parents=True, exist_ok=True)

    _write(target / "status.md", render_status(service, slug))
    _write(target / "probes.md", render_probes(service, slug))

    by_participant: dict[str, list[str]] = {}
    for post in service.store.posts(slug):
        by_participant.setdefault(post["participant"], []).append(render_post(service, post))
    for pid, chunks in by_participant.items():
        _write(target / f"from-{pid}.md", "".join(chunks).lstrip("\n"))

    t = service.store.thread(slug)
    if t and t.get("summary"):
        _write(target / "outcome.md", f"# Ergebnis\n\n{t['summary'].rstrip()}\n")
    return target
