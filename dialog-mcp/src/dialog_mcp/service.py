"""Zustandsautomat des Dialogs.

Identitaet ist hier immer ein ausdrueckliches Argument (`actor`). Wer der
Aufrufer ist, entscheidet die Transportschicht - beim MCP-Server das
Bearer-Token, in der Weboberflaeche die Sitzung. Damit laesst sich der
Automat vollstaendig ohne Server testen, und kein Agent kann seine Identitaet
ueber ein Werkzeug-Argument behaupten.

    dialog_open
         |
         v
    probing --(alle Sonden liegen)--> probe_review
                                         |
                        converged        |        diverged
                     +-------------------+------------------+
                     v                                      v
                   done  <---------- close ------------  debating
"""

from __future__ import annotations

import asyncio
import re
from typing import Any

from . import rules
from .store import Participant, Store
from .store import now as store_now

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


class DialogError(Exception):
    """Verstoss gegen den Ablauf - falscher Zustand, falsche Rolle, falscher Zug."""


def _evidence(items: Any) -> list[rules.Evidence]:
    out: list[rules.Evidence] = []
    for item in items or []:
        if not isinstance(item, dict):
            raise rules.RuleViolation("evidence", "§1", "Evidenz ist ein Objekt aus 'path' und 'locator'.")
        out.append(rules.Evidence(str(item.get("path", "")), str(item.get("locator", ""))))
    return out


class Service:
    def __init__(self, store: Store, export_dir: str | None = None) -> None:
        self.store = store
        self.export_dir = export_dir

    # -- Hilfen ---------------------------------------------------------

    def _thread(self, slug: str) -> dict[str, Any]:
        t = self.store.thread(slug)
        if t is None:
            raise DialogError(f"Thread {slug!r} existiert nicht.")
        return t

    def _actor(self, actor: str) -> Participant:
        p = self.store.participant(actor)
        if p is None:
            raise DialogError(f"Unbekannter Teilnehmer {actor!r}.")
        return p

    @staticmethod
    def _require_open(t: dict[str, Any]) -> None:
        if t["state"] == "done":
            raise DialogError(
                f"Thread {t['slug']!r} ist abgeschlossen. Ein abgeschlossener Thread ist terminal; "
                "fuer neuen Klaerungsbedarf einen neuen Thread anlegen."
            )

    def _is_owner(self, actor: str) -> bool:
        return self._actor(actor).role == "owner"

    # -- Anlegen --------------------------------------------------------

    def open_thread(
        self,
        actor: str,
        *,
        slug: str,
        topic: str,
        debaters: list[str],
        probers: list[str] | None = None,
        max_rounds: int = 3,
        profile: str = "strict",
    ) -> dict[str, Any]:
        self._actor(actor)
        if not SLUG_RE.match(slug or ""):
            raise DialogError("slug: nur Kleinbuchstaben, Ziffern und Bindestriche, hoechstens 64 Zeichen.")
        if self.store.thread(slug) is not None:
            raise DialogError(f"Thread {slug!r} existiert bereits.")
        if profile not in rules.PROFILES:
            raise DialogError(f"Unbekanntes Profil {profile!r}. Zulaessig: {', '.join(rules.PROFILES)}.")
        if len(debaters) != 2 or len(set(debaters)) != 2:
            raise DialogError("Genau zwei verschiedene Debattierende. Die Reihenfolge legt fest, wer beginnt.")
        if max_rounds < 1:
            raise DialogError("max_rounds muss mindestens 1 sein.")

        probers = list(dict.fromkeys((probers or []) + debaters))
        for pid in set(debaters) | set(probers):
            if self.store.participant(pid) is None:
                raise DialogError(f"Unbekannter Teilnehmer {pid!r}.")

        t = self.store.create_thread(
            slug=slug, topic=topic, profile=profile, debaters=debaters,
            probers=probers, max_rounds=max_rounds, opened_by=actor,
        )
        self.store.add_event(slug, "opened", actor, topic)
        return t

    # -- Sondenphase ----------------------------------------------------

    def submit_probe(self, actor: str, slug: str, artifact: str, evidence: Any = None) -> dict[str, Any]:
        who = self._actor(actor)
        t = self._thread(slug)
        self._require_open(t)
        if t["state"] != "probing":
            raise DialogError(f"Die Sondenphase von {slug!r} ist geschlossen (Zustand: {t['state']}).")
        if actor not in t["probers"]:
            raise DialogError(f"{actor!r} ist in diesem Thread nicht als Sondierender eingetragen.")

        existing = {p["participant"] for p in self.store.probes(slug, t["probe_round"])}
        if actor in existing:
            raise DialogError("Deine Sonde fuer diese Runde liegt bereits vor.")

        probe = rules.Probe(artifact=artifact, evidence=_evidence(evidence))
        rules.validate_probe(probe, t["profile"])
        self.store.add_probe(
            slug, actor, t["probe_round"], probe.artifact,
            [{"path": e.path, "locator": e.locator} for e in probe.evidence],
            who.is_human,
        )
        self.store.add_event(slug, "probe", actor, "Sonde eingereicht")

        submitted = {p["participant"] for p in self.store.probes(slug, t["probe_round"])}
        if submitted >= set(t["probers"]):
            self.store.update_thread(slug, state="probe_review")
            self.store.add_event(slug, "probes_complete", "system", "Alle Sonden liegen vor")
        return self.status(slug)

    def probe_results(self, actor: str, slug: str) -> dict[str, Any]:
        """Blindheit: Sonden werden erst ausgeliefert, wenn alle vorliegen.

        Waehrend der Phase nennt der Server nur, wer noch fehlt - das ist kein
        inhaltlicher Hinweis und haelt den Ablauf trotzdem steuerbar.
        """
        self._actor(actor)
        t = self._thread(slug)
        if t["state"] == "probing":
            submitted = {p["participant"] for p in self.store.probes(slug, t["probe_round"])}
            missing = [p for p in t["probers"] if p not in submitted]
            raise DialogError(
                "Die Sondenphase laeuft noch - Sonden bleiben verdeckt, bis alle vorliegen. "
                f"Es fehlen: {', '.join(missing)}."
            )
        probes = self.store.probes(slug, t["probe_round"])
        blocked = rules.convergence_blocked(self._probe_objects(probes))
        return {
            "slug": slug,
            "probe_round": t["probe_round"],
            "probes": probes,
            "convergence_possible": blocked is None,
            "convergence_blocked_because": blocked,
        }

    @staticmethod
    def _probe_objects(probes: list[dict[str, Any]]) -> dict[str, rules.Probe]:
        return {
            p["participant"]: rules.Probe(
                artifact=p["artifact"],
                evidence=[rules.Evidence(e["path"], e["locator"]) for e in p["evidence"]],
            )
            for p in probes
        }

    def resolve_probes(self, actor: str, slug: str, outcome: str, rationale: str) -> dict[str, Any]:
        who = self._actor(actor)
        t = self._thread(slug)
        self._require_open(t)
        if t["state"] != "probe_review":
            raise DialogError(f"Sonden koennen im Zustand {t['state']!r} nicht bewertet werden.")
        if who.role == "prober":
            raise DialogError("Nur Debattierende oder der Eigentuemer bewerten die Sondenphase.")
        if not (rationale or "").strip():
            raise DialogError("Die Bewertung der Sondenphase braucht eine Begruendung.")
        if outcome not in ("converged", "diverged", "repeat"):
            raise DialogError("outcome: 'converged', 'diverged' oder 'repeat'.")

        probes = self.store.probes(slug, t["probe_round"])
        if outcome == "converged":
            blocked = rules.convergence_blocked(self._probe_objects(probes))
            if blocked:
                raise DialogError(f"'converged' ist hier nicht zulaessig: {blocked}")
            self.store.update_thread(
                slug, state="done", turn=None, outcome="converged",
                summary=rationale, closed_at=store_now(),
            )
            self.store.add_event(slug, "converged", actor, rationale)
            self._export(slug)
        elif outcome == "repeat":
            self.store.update_thread(slug, state="probing", probe_round=t["probe_round"] + 1)
            self.store.add_event(slug, "probes_repeat", actor, rationale)
        else:
            self.store.update_thread(slug, state="debating", turn=t["debaters"][0], outcome="debated")
            self.store.add_event(slug, "diverged", actor, rationale)
        return self.status(slug)

    # -- Debatte --------------------------------------------------------

    def post(self, actor: str, slug: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._actor(actor)
        t = self._thread(slug)
        self._require_open(t)
        if t["state"] != "debating":
            raise DialogError(
                f"In {slug!r} laeuft keine Debatte (Zustand: {t['state']}). "
                "Die Sondenphase muss zuerst als divergent bewertet werden."
            )
        if t["turn"] is None:
            raise DialogError(
                "Die letzte Runde ist gesprochen. Der Thread wartet auf den Abschluss "
                "oder auf eine Verlaengerung durch den Eigentuemer."
            )
        if t["turn"] != actor:
            raise DialogError(f"{t['turn']!r} ist am Zug, nicht {actor!r}.")

        round_no = int(t["round"])
        is_final = round_no >= int(t["max_rounds"])
        post = rules.Post(
            body=str(payload.get("body", "")),
            evidence=_evidence(payload.get("evidence")),
            objections=[
                rules.Objection(
                    str(o.get("claim", "")), str(o.get("reasoning", "")), str(o.get("retract_if", ""))
                )
                for o in (payload.get("objections") or [])
            ],
            clearances=[
                rules.Clearance(
                    str(c.get("field", "")), str(c.get("reasoning", "")), str(c.get("retract_if", ""))
                )
                for c in (payload.get("clearances") or [])
            ],
            priorities=payload.get("priorities"),
            matrix=payload.get("matrix"),
            residual=payload.get("residual"),
            extension=str(payload.get("extension") or ""),
        )
        rules.validate_post(post, profile=t["profile"], round_no=round_no, is_final_round=is_final)

        self.store.add_post(slug, actor, round_no, {
            "body": post.body,
            "evidence": [{"path": e.path, "locator": e.locator} for e in post.evidence],
            "objections": [vars(o) for o in post.objections],
            "clearances": [vars(c) for c in post.clearances],
            "priorities": post.priorities,
            "matrix": post.matrix,
            "residual": post.residual,
            "extension": post.extension,
        })

        other = [d for d in t["debaters"] if d != actor][0]
        spoken = {p["participant"] for p in self.store.posts_in_round(slug, round_no)}
        if set(t["debaters"]) <= spoken:
            # debate-mode.md: der zweite Sprecher einer Runde erhoeht den Zaehler.
            if is_final:
                self.store.update_thread(slug, turn=None)
                self.store.add_event(slug, "debate_complete", "system", f"Runde {round_no} abgeschlossen")
            else:
                self.store.update_thread(slug, round=round_no + 1, turn=other)
                self.store.add_event(slug, "round", "system", f"Runde {round_no + 1} beginnt")
        else:
            self.store.update_thread(slug, turn=other)
        self.store.add_event(slug, "post", actor, f"Runde {round_no}")
        if post.extension:
            self.store.add_event(slug, "extension_recommended", actor, post.extension)
        return self.status(slug)

    # -- Advisory-Steuerung ---------------------------------------------

    def extend(self, actor: str, slug: str, extra_rounds: int, reason: str) -> dict[str, Any]:
        """debate-mode.md §4 - Agenten empfehlen, der Mensch entscheidet."""
        if not self._is_owner(actor):
            raise DialogError(
                "Nur der Eigentuemer verlaengert einen Dialog. Agenten empfehlen eine "
                "Verlaengerung im Feld 'extension' ihres Beitrags (Advisory-Modell)."
            )
        t = self._thread(slug)
        self._require_open(t)
        if extra_rounds < 1:
            raise DialogError("extra_rounds muss mindestens 1 sein.")
        new_max = int(t["max_rounds"]) + extra_rounds
        fields: dict[str, Any] = {"max_rounds": new_max}
        if t["state"] == "debating" and t["turn"] is None:
            last = self.store.posts(slug)[-1]["participant"]
            fields["round"] = int(t["round"]) + 1
            fields["turn"] = [d for d in t["debaters"] if d != last][0]
        self.store.update_thread(slug, **fields)
        self.store.add_event(slug, "extended", actor, f"+{extra_rounds}: {reason}")
        return self.status(slug)

    def repeat_probes(self, actor: str, slug: str, reason: str) -> dict[str, Any]:
        if not self._is_owner(actor):
            raise DialogError("Nur der Eigentuemer laesst die Sondenphase wiederholen.")
        t = self._thread(slug)
        self._require_open(t)
        self.store.update_thread(slug, state="probing", probe_round=int(t["probe_round"]) + 1, turn=None)
        self.store.add_event(slug, "probes_repeat", actor, reason)
        return self.status(slug)

    def close(self, actor: str, slug: str, summary: str) -> dict[str, Any]:
        who = self._actor(actor)
        t = self._thread(slug)
        self._require_open(t)
        if not (summary or "").strip():
            raise DialogError("Der Abschluss braucht eine Zusammenfassung.")
        if who.role != "owner":
            if t["state"] != "debating" or t["turn"] is not None:
                raise DialogError(
                    "Debattierende schliessen erst, wenn die letzte Runde gesprochen ist. "
                    "Vorzeitig schliesst nur der Eigentuemer."
                )
        self.store.update_thread(
            slug, state="done", turn=None, summary=summary,
            outcome=t["outcome"] or "debated", closed_at=store_now(),
        )
        self.store.add_event(slug, "closed", actor, summary)
        return {**self.status(slug), "export": self._export(slug)}

    # -- Lesen ----------------------------------------------------------

    def status(self, slug: str) -> dict[str, Any]:
        t = self._thread(slug)
        submitted = {p["participant"] for p in self.store.probes(slug, t["probe_round"])}
        return {
            "slug": t["slug"],
            "topic": t["topic"],
            "state": t["state"],
            "profile": t["profile"],
            "round": t["round"],
            "max_rounds": t["max_rounds"],
            "probe_round": t["probe_round"],
            "turn": t["turn"],
            "debaters": t["debaters"],
            "probers": t["probers"],
            "outcome": t["outcome"],
            "probes_missing": [p for p in t["probers"] if p not in submitted] if t["state"] == "probing" else [],
            "updated_at": t["updated_at"],
        }

    def listing(self, state: str | None = None) -> list[dict[str, Any]]:
        return [self.status(t["slug"]) for t in self.store.threads(state)]

    def read(self, actor: str, slug: str, since_round: int = 0) -> dict[str, Any]:
        self._actor(actor)
        t = self._thread(slug)
        out: dict[str, Any] = {"status": self.status(slug), "posts": self.store.posts(slug, since_round)}
        if t["state"] == "probing":
            out["probes"] = None
            out["probes_note"] = "Verdeckt bis alle Sonden vorliegen (§0)."
        else:
            out["probes"] = self.store.all_probes(slug)
        return out

    async def wait(self, actor: str, slug: str, timeout: float = 300.0, interval: float = 1.0) -> dict[str, Any]:
        """Long-Poll statt Polling durch den Agenten.

        Kehrt zurueck, sobald der Aufrufer am Zug ist, eine Sonde von ihm
        erwartet wird oder sich der Zustand des Threads aendert.
        """
        self._actor(actor)
        start = self._thread(slug)
        baseline = (start["state"], start["turn"], start["round"], start["probe_round"])
        deadline = asyncio.get_running_loop().time() + max(1.0, timeout)
        while True:
            t = self._thread(slug)
            if t["turn"] == actor:
                return {"reason": "your_turn", **self.status(slug)}
            if t["state"] == "probing" and actor in t["probers"]:
                submitted = {p["participant"] for p in self.store.probes(slug, t["probe_round"])}
                if actor not in submitted:
                    return {"reason": "probe_due", **self.status(slug)}
            current = (t["state"], t["turn"], t["round"], t["probe_round"])
            if current != baseline:
                return {"reason": "state_changed", **self.status(slug)}
            if asyncio.get_running_loop().time() >= deadline:
                return {"reason": "timeout", **self.status(slug)}
            await asyncio.sleep(interval)

    # -- Export ---------------------------------------------------------

    def _export(self, slug: str) -> str | None:
        if not self.export_dir:
            return None
        from .export import write_export

        return str(write_export(self, slug, self.export_dir))
