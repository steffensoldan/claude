"""Die HTML-Datei: Liveticker waehrend des Dialogs, Dokument danach.

Kein JavaScript, keine externen Assets. Solange der Dialog laeuft, traegt die
Seite ein Meta-Refresh und laedt sich selbst nach; beim Abschluss faellt es weg,
damit das fertige Dokument ruhig liegen bleibt.
"""

from __future__ import annotations

from html import escape
from typing import Any

from .thread import DATA_CLOSE, DATA_OPEN, encode_data

REFRESH_SECONDS = 5

STYLE = """
:root {
  --paper:#f3f3f0; --card:#fff; --ink:#191b20; --muted:#636872; --rule:#dad9d2;
  --accent:#1f5aa6; --ok:#2c6e52; --warn:#8a6410;
}
@media (prefers-color-scheme: dark) {
  :root { --paper:#14161a; --card:#1c1f25; --ink:#e7e7e2; --muted:#949aa4; --rule:#333844;
          --accent:#7faadf; --ok:#7fc5a2; --warn:#d9b663; }
}
* { box-sizing:border-box; }
body { margin:0; background:var(--paper); color:var(--ink); line-height:1.55;
       font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; }
main { max-width:820px; margin:0 auto; padding:32px 20px 72px; }
h1 { font-size:1.65rem; line-height:1.2; margin:0 0 10px; }
h2 { font-size:1.05rem; margin:32px 0 12px; }
h3 { font-size:.95rem; margin:0 0 6px; }
code { font-family:ui-monospace,Menlo,Consolas,monospace; font-size:.88em; }
.meta { color:var(--muted); font-size:.92rem; margin:0 0 4px; }
.pill { display:inline-block; font-size:.72rem; text-transform:uppercase; letter-spacing:.07em;
        border:1px solid var(--rule); padding:2px 8px; }
.pill.probing { color:var(--warn); } .pill.probe_review { color:var(--accent); }
.pill.debating { color:var(--ink); } .pill.done { color:var(--ok); }
.card { background:var(--card); border:1px solid var(--rule); padding:18px 20px; margin:0 0 16px; }
.post .who { font-weight:700; }
.post .stamp { color:var(--muted); font-size:.85rem; font-weight:400; }
.body { white-space:pre-wrap; margin:10px 0 0; }
.obj { border-left:2px solid var(--accent); padding-left:14px; margin:14px 0 0; }
.obj .claim { font-weight:600; }
.retract { color:var(--accent); font-size:.92rem; }
.result { border:1px solid var(--accent); background:var(--card); padding:18px 20px; margin:24px 0 0; }
.hidden-note { color:var(--muted); font-style:italic; }
.artifact { font-family:ui-monospace,Menlo,Consolas,monospace; font-size:.9rem; white-space:pre-wrap;
            background:var(--paper); border:1px solid var(--rule); padding:10px 12px; margin:8px 0 0; }
.turn { font-weight:700; }
footer { max-width:820px; margin:0 auto; padding:16px 20px 48px; border-top:1px solid var(--rule);
         color:var(--muted); font-size:.8rem; }
"""


def _stamp(iso: str) -> str:
    return iso.replace("T", " ")[:16]


def _post_html(post: dict[str, Any]) -> str:
    parts = [
        '<article class="card post">',
        f'<h3><span class="who">{escape(post["who"])}</span> '
        f'<span class="stamp">Runde {post["round"]} · {escape(_stamp(post["at"]))}</span></h3>',
        f'<div class="body">{escape(post["body"])}</div>',
    ]
    for obj in post.get("objections") or []:
        parts.append(
            '<div class="obj">'
            f'<div class="claim">{escape(obj["claim"])}</div>'
            f'<div class="retract">Ich ziehe das zurück, wenn: {escape(obj["retract_if"])}</div>'
            "</div>"
        )
    parts.append("</article>")
    return "\n".join(parts)


def _probes_html(data: dict[str, Any]) -> str:
    state = data["state"]
    if state in ("probing", "probe_review"):
        eingegangen = [p for p in data["participants"] if p not in data["probes_pending"]]
        fehlen = data["probes_pending"]
        note = (
            f"Eingegangen: {escape(', '.join(eingegangen)) or '—'}. "
            + (f"Es fehlt: {escape(', '.join(fehlen))}." if fehlen else "Vollzählig — bereit zur Bewertung.")
        )
        return (
            '<h2>Sondenphase</h2><div class="card">'
            f'<p class="hidden-note">Die Artefakte bleiben verdeckt, bis die Phase aufgelöst ist.</p>'
            f"<p>{note}</p></div>"
        )

    if not data.get("probes"):
        return ""

    parts = ["<h2>Sondenphase</h2>"]
    for probe in data["probes"]:
        parts.append(
            '<div class="card">'
            f'<h3>{escape(probe["who"])} <span class="stamp">{escape(_stamp(probe["at"]))}</span></h3>'
            f'<div class="artifact">{escape(probe["artifact"])}</div></div>'
        )
    outcome = data.get("probe_outcome")
    if outcome:
        label = "Übereinstimmend — keine Debatte nötig" if outcome["outcome"] == "converged" else "Divergent — Debatte eröffnet"
        parts.append(
            f'<div class="card"><h3>{label}</h3>'
            f'<div class="body">{escape(outcome["rationale"])}</div>'
            f'<p class="meta">bewertet von {escape(outcome["by"])} · {escape(_stamp(outcome["at"]))}</p></div>'
        )
    return "\n".join(parts)


def render(data: dict[str, Any]) -> str:
    done = data["state"] == "done"
    refresh = "" if done else f'\n  <meta http-equiv="refresh" content="{REFRESH_SECONDS}">'

    if done:
        standline = "Abgeschlossen"
    elif data["state"] == "debating":
        standline = f'Am Zug: <span class="turn">{escape(data["turn"] or "—")}</span>'
    else:
        standline = "Sondenphase läuft"

    body = [
        f"<h1>{escape(data['topic'])}</h1>",
        f'<p class="meta"><code>{escape(data["slug"])}</code> · '
        f'<span class="pill {data["state"]}">{data["state"]}</span> · '
        f'Runde {data["round"]}/{data["max_rounds"]} · '
        f'{escape(" gegen ".join(data["participants"]))}</p>',
        f'<p class="meta">{standline} · Stand {escape(_stamp(data["updated"]))}</p>',
        _probes_html(data),
    ]

    if data["posts"]:
        body.append("<h2>Verlauf</h2>")
        body.extend(_post_html(p) for p in data["posts"])

    result = data.get("result")
    if result:
        body.append(
            '<div class="result"><h2 style="margin-top:0">Ergebnis</h2>'
            f'<div class="body">{escape(result["summary"])}</div>'
            f'<p class="meta">{escape(result["by"])} · {escape(_stamp(result["at"]))}</p></div>'
        )

    ticker_note = (
        "Diese Seite lädt sich alle paar Sekunden neu, solange der Dialog läuft."
        if not done
        else "Dialog abgeschlossen — die Seite lädt sich nicht mehr neu."
    )

    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(data['topic'])} — Agent-Dialog</title>{refresh}
  {DATA_OPEN}
{encode_data(data)}
  {DATA_CLOSE}
  <style>{STYLE}</style>
</head>
<body>
<main>
{chr(10).join(part for part in body if part)}
</main>
<footer>
  {ticker_note} Der vollständige Zustand liegt als JSON im Kopf dieser Datei —
  sie ist zugleich Speicher, Mitleseansicht und Abschlussdokument.
</footer>
</body>
</html>
"""
