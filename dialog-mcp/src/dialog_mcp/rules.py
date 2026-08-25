"""Umsetzung der inhaltlichen Regeln aus AOS `memory/debate-mode.md`.

Diese Datei ist die einzige Stelle, an der entschieden wird, ob ein Beitrag oder
eine Sonde den Debattenmodus erfuellt. MCP-Server und Weboberflaeche rufen sie
beide auf; es gibt keine zweite Regelquelle.

Kein Import aus dem MCP-SDK - die Regeln sind ohne Server testbar.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# debate-mode.md §3 - die fuenf Dimensionen der Kriterien-Matrix.
DIMENSIONS = ("sicherheit", "robustheit", "wartbarkeit", "usability", "compliance")

# debate-mode.md §1 - die fuenf Risikofelder der Entwarnungs-Ausnahme.
RISK_FIELDS = ("netzwerk", "daten", "plattform", "berechtigungen", "ressourcen")

PROFILES = ("strict", "light")

# In diesen Runden verlangt §1 zwingend einen Einwand oder eine Entwarnung.
OBJECTION_ROUNDS = (1, 2)


class RuleViolation(Exception):
    """Ein Beitrag verletzt den Debattenmodus.

    `field` benennt das beanstandete Feld, `rule` den Paragraphen aus
    debate-mode.md. Beides geht woertlich an den Agenten zurueck, damit er
    nachbessern kann, statt zu raten.
    """

    def __init__(self, field: str, rule: str, message: str) -> None:
        super().__init__(f"[{field}] {message} (debate-mode.md {rule})")
        self.field = field
        self.rule = rule
        self.message = message


@dataclass
class Evidence:
    """Eine beruehrte Stelle: Datei plus Fundort darin."""

    path: str
    locator: str

    def key(self) -> tuple[str, str]:
        return (self.path.strip().lower(), self.locator.strip().lower())


@dataclass
class Objection:
    claim: str
    reasoning: str
    retract_if: str = ""


@dataclass
class Clearance:
    """Entwarnung nach §1: ein Risikofeld, begruendet, mit Ruecknahmebedingung."""

    field: str
    reasoning: str
    retract_if: str = ""


@dataclass
class Post:
    body: str
    evidence: list[Evidence] = field(default_factory=list)
    objections: list[Objection] = field(default_factory=list)
    clearances: list[Clearance] = field(default_factory=list)
    priorities: dict[str, Any] | None = None
    matrix: dict[str, Any] | None = None
    residual: dict[str, Any] | None = None
    extension: str = ""


@dataclass
class Probe:
    artifact: str
    evidence: list[Evidence] = field(default_factory=list)


def _require_text(value: Any, field_name: str, rule: str, what: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RuleViolation(field_name, rule, what)
    return value.strip()


def normalize_artifact(artifact: str) -> str:
    """Vergleichsform eines Sonden-Artefakts.

    Bewusst mechanisch: Kleinschreibung und zusammengezogene Leerraeume. Der
    Server faellt kein inhaltliches Urteil ueber Gleichheit - er prueft nur,
    ob zwei Artefakte buchstaeblich dasselbe sagen.
    """
    return " ".join(artifact.lower().split())


def validate_probe(probe: Probe, profile: str) -> None:
    """§0 - Artefakt statt Prosa, und Evidenzkontakt ist Pflicht."""
    _require_text(probe.artifact, "artifact", "§0", "Die Sonde braucht ein Artefakt.")
    if profile == "light":
        return
    if not probe.evidence:
        raise RuleViolation(
            "evidence",
            "§0",
            "Die Sonde nennt keine beruehrte Evidenz. Eine Sonde ohne "
            "Evidenzkontakt hat nur den Prior des Modells gezogen.",
        )
    for item in probe.evidence:
        _require_text(item.path, "evidence[].path", "§0", "Jede Evidenz braucht eine Datei.")
        _require_text(item.locator, "evidence[].locator", "§0", "Jede Evidenz braucht eine Stelle in der Datei.")


def convergence_blocked(probes: dict[str, Probe]) -> str | None:
    """Prueft, ob `converged` mechanisch zulaessig waere.

    Gibt den Ablehnungsgrund zurueck oder None, wenn nichts entgegensteht. Die
    Bewertung selbst faellt ein Debattierender - der Server verhindert nur die
    beiden Faelle, in denen Einigkeit nachweislich nichts wert ist.
    """
    if len(probes) < 2:
        return "Weniger als zwei Sonden liegen vor."

    artifacts = {normalize_artifact(p.artifact) for p in probes.values()}
    if len(artifacts) > 1:
        return "Die Artefakte unterscheiden sich - das ist Divergenz, keine Konvergenz."

    if any(not p.evidence for p in probes.values()):
        return (
            "Mindestens eine Sonde hat keine Evidenz beruehrt. Uebereinstimmung "
            "ist hier geteilter Prior, kein Konsens (§0)."
        )

    locators = {item.key() for p in probes.values() for item in p.evidence}
    if len(locators) < 2:
        return (
            "Alle Sonden haben nur dieselbe einzelne Stelle beruehrt. "
            "Uebereinstimmung belegt damit keinen unabhaengigen Befund (§0)."
        )
    return None


def _validate_objections(post: Post, round_no: int) -> None:
    for obj in post.objections:
        _require_text(obj.claim, "objections[].claim", "§1", "Ein Einwand braucht eine Aussage.")
        _require_text(obj.reasoning, "objections[].reasoning", "§1", "Ein Einwand braucht eine Begruendung.")
        _require_text(
            obj.retract_if,
            "objections[].retract_if",
            "§1",
            "Jeder Einwand endet mit 'Ich ziehe das zurueck, wenn ___'. Wer das "
            "Feld nicht fuellen kann, hat ein Stilmittel geliefert, keinen Einwand.",
        )

    for cl in post.clearances:
        if cl.field.strip().lower() not in RISK_FIELDS:
            raise RuleViolation(
                "clearances[].field",
                "§1",
                f"Unbekanntes Risikofeld {cl.field!r}. Zulaessig: {', '.join(RISK_FIELDS)}.",
            )
        _require_text(cl.reasoning, "clearances[].reasoning", "§1", "Eine Entwarnung braucht eine Begruendung.")
        _require_text(
            cl.retract_if,
            "clearances[].retract_if",
            "§1",
            "Auch die Entwarnung traegt ihre Ruecknahmebedingung: "
            "'Diese Entwarnung faellt, wenn ___'.",
        )

    if round_no not in OBJECTION_ROUNDS:
        return

    if post.objections:
        return

    if len(post.clearances) < 2:
        raise RuleViolation(
            "objections",
            "§1",
            "In Runde 1 und 2 ist mindestens ein Einwand zwingend. Liegt kein "
            "Risiko vor, sind stattdessen die zwei kritischsten der fuenf "
            "Risikofelder als Entwarnung zu benennen und zu begruenden.",
        )
    if len({c.field.strip().lower() for c in post.clearances}) < 2:
        raise RuleViolation(
            "clearances",
            "§1",
            "Die Entwarnung muss zwei verschiedene Risikofelder abdecken.",
        )


def _validate_priorities(post: Post) -> None:
    if not isinstance(post.priorities, dict):
        raise RuleViolation(
            "priorities",
            "§3",
            "Jeder Beitrag deklariert seine Priorisierung: bis zu zwei "
            "Dimensionen plus das Opfer an der eigenen Loesung.",
        )
    dims = post.priorities.get("dimensions") or []
    if not isinstance(dims, list) or not dims:
        raise RuleViolation("priorities.dimensions", "§3", "Mindestens eine priorisierte Dimension angeben.")
    if len(dims) > 2:
        raise RuleViolation("priorities.dimensions", "§3", "Hoechstens zwei Dimensionen duerfen priorisiert werden.")
    for dim in dims:
        key = str(dim).strip().lower()
        if key not in DIMENSIONS:
            raise RuleViolation(
                "priorities.dimensions",
                "§3",
                f"Unbekannte Dimension {dim!r}. Zulaessig: {', '.join(DIMENSIONS)}.",
            )
        if key == "compliance":
            raise RuleViolation(
                "priorities.dimensions",
                "§3",
                "Compliance ist von der Priorisierung ausgenommen - das Gate ist "
                "in jeder Runde vollstaendig zu pruefen und nicht abwaegbar.",
            )
    _require_text(
        post.priorities.get("sacrifice"),
        "priorities.sacrifice",
        "§3",
        "Benenne, welchen Teil deiner eigenen Loesung diese Priorisierung kostet. "
        "Eine Prioritaet, die den eigenen Entwurf nichts kostet, ist eine Behauptung.",
    )


def _validate_matrix(post: Post) -> None:
    if not isinstance(post.matrix, dict):
        raise RuleViolation("matrix", "§3", "Die fuenfdimensionale Kriterien-Matrix fehlt.")
    missing = [d for d in DIMENSIONS if d not in {k.strip().lower() for k in post.matrix}]
    if missing:
        raise RuleViolation("matrix", "§3", f"Fehlende Dimensionen: {', '.join(missing)}.")
    lowered = {k.strip().lower(): v for k, v in post.matrix.items()}
    for dim in DIMENSIONS:
        cell = lowered[dim]
        if not isinstance(cell, dict):
            raise RuleViolation(f"matrix.{dim}", "§3", "Jede Dimension braucht 'rating' und 'note'.")
        _require_text(cell.get("rating"), f"matrix.{dim}.rating", "§3", "Bewertung fehlt.")
        _require_text(cell.get("note"), f"matrix.{dim}.note", "§3", "Begruendung fehlt.")
    gate = lowered["compliance"].get("gate")
    if gate not in ("bestanden", "blockiert"):
        raise RuleViolation(
            "matrix.compliance.gate",
            "§3",
            "Das Compliance-Gate ist mit 'bestanden' oder 'blockiert' zu beantworten.",
        )
    if gate == "blockiert" and not (lowered["compliance"].get("blockers") or []):
        raise RuleViolation(
            "matrix.compliance.blockers",
            "§3",
            "Ein blockiertes Gate muss die verletzten Hard-Blocker benennen.",
        )


def _validate_residual(post: Post) -> None:
    if not isinstance(post.residual, dict):
        raise RuleViolation(
            "residual",
            "§4",
            "Die Abschlussrunde enthaelt den Pflichtabschnitt 'Ungeloeste Restdifferenz'. "
            "'Wir sind uns einig' allein ist kein zulaessiger Abschluss.",
        )
    _require_text(post.residual.get("difference"), "residual.difference", "§4", "Benenne die ungeloeste Stelle.")
    _require_text(
        post.residual.get("why_unresolvable"),
        "residual.why_unresolvable",
        "§4",
        "Begruende, warum weiteres Argumentieren die Stelle nicht entscheidet.",
    )
    _require_text(
        post.residual.get("measurement"),
        "residual.measurement",
        "§4",
        "Nenne die Messung oder das Experiment, das die Differenz entscheiden wuerde.",
    )


def validate_post(post: Post, *, profile: str, round_no: int, is_final_round: bool) -> None:
    """Prueft einen Beitrag gegen das Profil des Threads.

    Wirft die erste `RuleViolation`, die greift. Reihenfolge ist bewusst
    inhaltlich sortiert: erst Substanz, dann Form.
    """
    if profile not in PROFILES:
        raise RuleViolation("profile", "§0", f"Unbekanntes Profil {profile!r}.")

    _require_text(post.body, "body", "§5", "Der Beitrag ist leer.")

    if profile == "light":
        return

    if not post.evidence:
        raise RuleViolation(
            "evidence",
            "§1",
            "Jeder Beitrag nennt die Dateien und Stellen, auf die er sich stuetzt. "
            "Behauptungen ohne Evidenzangabe zaehlen nicht als geprueft.",
        )
    for item in post.evidence:
        _require_text(item.path, "evidence[].path", "§1", "Jede Evidenz braucht eine Datei.")
        _require_text(item.locator, "evidence[].locator", "§1", "Jede Evidenz braucht eine Stelle in der Datei.")

    _validate_objections(post, round_no)
    _validate_priorities(post)
    _validate_matrix(post)

    if is_final_round:
        _validate_residual(post)
