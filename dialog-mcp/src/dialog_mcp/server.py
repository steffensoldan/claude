"""MCP-Adapter: duenne Huelle um `Service`.

Jedes Werkzeug loest zuerst die Identitaet aus dem Bearer-Token auf und reicht
sie an den Zustandsautomaten weiter. Fachliche Logik steht hier nicht.
"""

from __future__ import annotations

from typing import Any

from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.settings import AuthSettings
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from .auth import Config, StaticTokenVerifier
from .rules import DIMENSIONS, RISK_FIELDS, RuleViolation
from .service import DialogError, Service

INSTRUCTIONS = f"""\
Regelgebundener Dialog zwischen zwei Agenten nach dem AOS-Debattenmodus.

Ablauf: dialog_open -> alle Beteiligten reichen blind eine Sonde ein
(dialog_probe_submit) -> dialog_probe_results -> dialog_probe_resolve entscheidet,
ob ueberhaupt debattiert wird -> dialog_post im Wechsel -> dialog_close.

Im Profil 'strict' weist der Server Beitraege zurueck, die den Debattenmodus
verletzen. Die Fehlermeldung nennt Feld und Paragraphen; bessere nach, statt zu
raten. Pflicht sind dort je Beitrag: Evidenzangaben, zu jedem Einwand eine
Ruecknahmebedingung ("Ich ziehe das zurueck, wenn ___"), eine deklarierte
Priorisierung mit benanntem Opfer an der eigenen Loesung, die Kriterien-Matrix
ueber {', '.join(DIMENSIONS)} - und in der letzten Runde die ungeloeste
Restdifferenz samt Messdesign.

Deine Identitaet steht im Token und ist kein Argument. Warte mit dialog_wait,
statt zu pollen.
"""


def _actor() -> str:
    token = get_access_token()
    if token is None or not token.subject:
        raise ToolError("Nicht authentifiziert - es fehlt ein gueltiges Bearer-Token.")
    return token.subject


def build_server(config: Config, service: Service) -> MCPServer:
    mcp = MCPServer(
        name="aos-dialog",
        title="AOS Agent-Dialog",
        instructions=INSTRUCTIONS,
        version="0.1.0",
        token_verifier=StaticTokenVerifier(config.participants),
        auth=AuthSettings(
            issuer_url=config.public_url,
            resource_server_url=config.public_url,
            required_scopes=["dialog"],
        ),
    )

    def guard(fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except RuleViolation as exc:
            raise ToolError(str(exc)) from exc
        except DialogError as exc:
            raise ToolError(str(exc)) from exc

    @mcp.tool(
        name="dialog_open",
        description=(
            "Legt einen Dialog-Thread an und startet die Sondenphase. `debaters` sind genau zwei "
            "Teilnehmer-IDs; die Reihenfolge legt fest, wer die Debatte eroeffnet. `probers` sind "
            "zusaetzliche Sondierende (die Debattierenden sondieren immer mit). Profil 'strict' "
            "erzwingt den vollen Debattenmodus, 'light' nur einen nicht-leeren Beitrag."
        ),
    )
    def dialog_open(
        slug: str,
        topic: str,
        debaters: list[str],
        probers: list[str] | None = None,
        max_rounds: int = 3,
        profile: str = "strict",
    ) -> dict[str, Any]:
        return guard(
            service.open_thread,
            _actor(), slug=slug, topic=topic, debaters=debaters,
            probers=probers, max_rounds=max_rounds, profile=profile,
        )

    @mcp.tool(
        name="dialog_list",
        description="Listet Threads mit Zustand, Runde und der Angabe, wer am Zug ist. Optional nach Zustand gefiltert.",
    )
    def dialog_list(state: str | None = None) -> list[dict[str, Any]]:
        return service.listing(state)

    @mcp.tool(name="dialog_status", description="Kompakter Zustand eines Threads.")
    def dialog_status(slug: str) -> dict[str, Any]:
        return guard(service.status, slug)

    @mcp.tool(
        name="dialog_read",
        description=(
            "Vollstaendiger Verlauf eines Threads, optional erst ab Runde `since_round`. "
            "Solange die Sondenphase laeuft, bleiben alle Sonden verdeckt."
        ),
    )
    def dialog_read(slug: str, since_round: int = 0) -> dict[str, Any]:
        return guard(service.read, _actor(), slug, since_round)

    @mcp.tool(
        name="dialog_probe_submit",
        description=(
            "Reicht die eigene blinde Erstloesung ein - bevor du irgendetwas vom anderen gelesen hast. "
            "`artifact` ist ein Artefakt, keine Prosa: Datei und Zeile, ein Testfall, eine konkrete "
            "Entscheidung, eine Zahl; Richtwert hoechstens zehn Zeilen. `evidence` listet die "
            "tatsaechlich gelesenen Stellen als [{'path': ..., 'locator': ...}]. Eine Sonde ohne "
            "Evidenzkontakt zieht nur den Prior des Modells und wird zurueckgewiesen."
        ),
    )
    def dialog_probe_submit(
        slug: str, artifact: str, evidence: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        return guard(service.submit_probe, _actor(), slug, artifact, evidence)

    @mcp.tool(
        name="dialog_probe_results",
        description=(
            "Zeigt alle Sonden - erst wenn jede vorliegt - und ob eine Bewertung als 'converged' "
            "mechanisch zulaessig waere."
        ),
    )
    def dialog_probe_results(slug: str) -> dict[str, Any]:
        return guard(service.probe_results, _actor(), slug)

    @mcp.tool(
        name="dialog_probe_resolve",
        description=(
            "Bewertet die Sondenphase mit Begruendung. 'converged' schliesst den Thread ohne Debatte "
            "und ist nur zulaessig, wenn die Artefakte uebereinstimmen UND jede Sonde unabhaengig "
            "Evidenz beruehrt hat. 'diverged' startet die Debatte; die Differenz der Sonden ist die "
            "Tagesordnung von Runde 1. 'repeat' laesst blind neu sondieren."
        ),
    )
    def dialog_probe_resolve(slug: str, outcome: str, rationale: str) -> dict[str, Any]:
        return guard(service.resolve_probes, _actor(), slug, outcome, rationale)

    @mcp.tool(
        name="dialog_post",
        description=(
            "Beitrag in der laufenden Runde; nur wer am Zug ist, kann schreiben. Im Profil 'strict' "
            "sind Pflicht: `evidence` (beruehrte Stellen), zu jedem Eintrag in `objections` die "
            "`retract_if`-Bedingung, `priorities` mit hoechstens zwei Dimensionen und `sacrifice`, "
            "sowie `matrix` ueber alle fuenf Dimensionen (Compliance mit 'gate'). In Runde 1 und 2 "
            "ist mindestens ein Einwand zwingend - liegt kein Risiko vor, stattdessen `clearances` "
            f"zu zwei der Risikofelder ({', '.join(RISK_FIELDS)}), jeweils mit Ruecknahmebedingung. "
            "In der letzten Runde ist `residual` mit difference/why_unresolvable/measurement Pflicht. "
            "`extension` empfiehlt eine Verlaengerung - entscheiden tut das der Eigentuemer."
        ),
    )
    def dialog_post(
        slug: str,
        body: str,
        evidence: list[dict[str, Any]] | None = None,
        objections: list[dict[str, Any]] | None = None,
        clearances: list[dict[str, Any]] | None = None,
        priorities: dict[str, Any] | None = None,
        matrix: dict[str, Any] | None = None,
        residual: dict[str, Any] | None = None,
        extension: str = "",
    ) -> dict[str, Any]:
        return guard(
            service.post, _actor(), slug,
            {
                "body": body, "evidence": evidence, "objections": objections,
                "clearances": clearances, "priorities": priorities, "matrix": matrix,
                "residual": residual, "extension": extension,
            },
        )

    @mcp.tool(
        name="dialog_wait",
        description=(
            "Blockiert, bis du am Zug bist, eine Sonde von dir erwartet wird oder sich der Zustand "
            "aendert - hoechstens `timeout` Sekunden. Nutze das statt wiederholtem dialog_status."
        ),
    )
    async def dialog_wait(slug: str, timeout: float = 300.0) -> dict[str, Any]:
        actor = _actor()
        try:
            return await service.wait(actor, slug, timeout)
        except DialogError as exc:
            raise ToolError(str(exc)) from exc

    @mcp.tool(
        name="dialog_close",
        description=(
            "Schliesst den Thread mit Zusammenfassung und schreibt den Export im AOS-Format. "
            "Debattierende koennen erst schliessen, wenn die letzte Runde gesprochen ist; "
            "vorzeitig schliesst nur der Eigentuemer. Ein geschlossener Thread ist terminal."
        ),
    )
    def dialog_close(slug: str, summary: str) -> dict[str, Any]:
        return guard(service.close, _actor(), slug, summary)

    return mcp
