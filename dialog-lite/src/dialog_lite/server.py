"""Die sieben Werkzeuge - duenn ueber `thread.py`.

Identitaet kommt aus `--as` beim Start des Prozesses und ist kein Argument.
Das ist kein Nachweis wie ein Token, aber es haelt die Werkzeuge sauber: kein
Agent gibt beim Aufruf an, wer er zu sein behauptet.
"""

from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from . import thread
from .thread import DialogError

INSTRUCTIONS = """\
Dialog mit einem zweiten Agenten, in einer HTML-Datei je Thema.

Ablauf: dialog_open -> beide reichen blind dialog_probe ein -> dialog_probe_resolve
entscheidet, ob ueberhaupt debattiert wird -> dialog_post im Wechsel -> dialog_close.

Drei Regeln setzt der Server durch: nur wer am Zug ist schreibt, kein leerer Beitrag,
und jeder Einwand braucht seine Ruecknahmebedingung ("Ich ziehe das zurueck, wenn ___").
Wer die nicht angeben kann, hat keinen Einwand, sondern ein Stilmittel.

Die Sonde ist ein Artefakt, keine Prosa: Datei und Zeile, ein Testfall, eine konkrete
Entscheidung, eine Zahl. Fremde Sonden bleiben verdeckt, bis alle vorliegen.

Wer du bist, steht im Start des Servers - du gibst es bei keinem Aufruf an.
"""


def build_server(directory: str, me: str) -> MCPServer:
    mcp = MCPServer(
        name="dialog-lite",
        title=f"Agent-Dialog ({me})",
        instructions=INSTRUCTIONS,
        version="0.1.0",
    )

    def guard(fn, **kwargs):
        try:
            return fn(directory, me=me, **kwargs)
        except DialogError as exc:
            raise ToolError(str(exc)) from exc

    @mcp.tool(
        name="dialog_open",
        description=(
            "Legt einen Dialog an und startet die Sondenphase. `partner` ist die Kennung des anderen "
            "Agenten, so wie dessen Server gestartet wurde. Es entsteht eine HTML-Datei <slug>.html, "
            "die sich im Browser mitlesen laesst."
        ),
    )
    def dialog_open(slug: str, topic: str, partner: str, max_rounds: int = 3) -> dict[str, Any]:
        return thread.summary(
            guard(thread.open_thread, slug=slug, topic=topic, partner=partner, max_rounds=max_rounds)
        )

    @mcp.tool(name="dialog_list", description="Alle Dialoge im Ordner mit Zustand und wer am Zug ist.")
    def dialog_list() -> list[dict[str, Any]]:
        return thread.list_threads(directory)

    @mcp.tool(
        name="dialog_read",
        description=(
            "Voller Verlauf eines Dialogs. Solange die Sondenphase laeuft, bleibt das Artefakt des "
            "anderen verdeckt - genannt wird nur, wessen Sonde noch fehlt."
        ),
    )
    def dialog_read(slug: str) -> dict[str, Any]:
        return guard(thread.read, slug=slug)

    @mcp.tool(
        name="dialog_probe",
        description=(
            "Deine blinde Erstloesung, bevor du irgendetwas vom anderen gelesen hast. Ein Artefakt, "
            "keine Prosa: Datei und Zeile, ein Testfall, eine konkrete Entscheidung, eine Zahl. "
            "Richtwert hoechstens zehn Zeilen. Stimmen die Artefakte spaeter ueberein, ist die Debatte "
            "unnoetig - genau dafuer ist die Sonde da."
        ),
    )
    def dialog_probe(slug: str, artifact: str) -> dict[str, Any]:
        return thread.summary(guard(thread.submit_probe, slug=slug, artifact=artifact))

    @mcp.tool(
        name="dialog_probe_resolve",
        description=(
            "Bewertet die Sondenphase, sobald beide Sonden vorliegen. 'converged' beendet den Dialog "
            "ohne Debatte, 'diverged' eroeffnet sie - die Differenz der Sonden ist dann die "
            "Tagesordnung von Runde 1. Begruendung ist Pflicht."
        ),
    )
    def dialog_probe_resolve(slug: str, outcome: str, rationale: str) -> dict[str, Any]:
        return thread.summary(guard(thread.resolve_probes, slug=slug, outcome=outcome, rationale=rationale))

    @mcp.tool(
        name="dialog_post",
        description=(
            "Beitrag in der laufenden Runde - nur wer am Zug ist, kann schreiben. `objections` ist eine "
            "Liste aus {'claim': ..., 'retract_if': ...}; ohne Ruecknahmebedingung wird der Beitrag "
            "abgelehnt. Nach dem zweiten Sprecher einer Runde zaehlt die Runde hoch."
        ),
    )
    def dialog_post(slug: str, body: str, objections: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        return thread.summary(guard(thread.post, slug=slug, body=body, objections=objections))

    @mcp.tool(
        name="dialog_close",
        description=(
            "Schliesst den Dialog mit einem Ergebnis in eigenen Worten. Danach ist der Thread terminal "
            "und die HTML-Datei laedt sich nicht mehr selbst nach."
        ),
    )
    def dialog_close(slug: str, summary: str) -> dict[str, Any]:
        return thread.summary(guard(thread.close, slug=slug, summary_text=summary))

    return mcp
