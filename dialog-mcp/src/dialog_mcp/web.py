"""Weboberflaeche: mitlesen, selbst sondieren, Advisory-Steuerung.

Laeuft im selben Prozess wie der MCP-Endpunkt und auf denselben Regeln - es
gibt keine zweite Regelquelle. Sitzungen liegen im Arbeitsspeicher: ein
Neustart des Dienstes erzwingt eine neue Anmeldung, dafuer gibt es kein
Signaturgeheimnis, das verwaltet oder rotiert werden muesste.
"""

from __future__ import annotations

import asyncio
import json
import secrets
from pathlib import Path
from typing import Any

from starlette.requests import Request
from starlette.responses import HTMLResponse, PlainTextResponse, RedirectResponse, StreamingResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from .auth import StaticTokenVerifier
from .rules import RuleViolation
from .service import DialogError, Service

HERE = Path(__file__).parent
COOKIE = "dialog_session"


class Sessions:
    def __init__(self) -> None:
        self._by_id: dict[str, dict[str, str]] = {}

    def create(self, participant_id: str) -> str:
        sid = secrets.token_urlsafe(32)
        self._by_id[sid] = {"participant": participant_id, "csrf": secrets.token_urlsafe(24)}
        return sid

    def get(self, sid: str | None) -> dict[str, str] | None:
        return self._by_id.get(sid) if sid else None

    def drop(self, sid: str | None) -> None:
        if sid:
            self._by_id.pop(sid, None)


def build_web(service: Service, verifier: StaticTokenVerifier) -> list[Route | Mount]:
    templates = Jinja2Templates(directory=str(HERE / "templates"))
    sessions = Sessions()

    def session_of(request: Request) -> dict[str, str] | None:
        return sessions.get(request.cookies.get(COOKIE))

    def actor_of(request: Request) -> str | None:
        sess = session_of(request)
        return sess["participant"] if sess else None

    def render(request: Request, name: str, ctx: dict[str, Any], status: int = 200) -> HTMLResponse:
        actor = actor_of(request)
        who = service.store.participant(actor) if actor else None
        sess = session_of(request)
        return templates.TemplateResponse(
            request, name,
            {**ctx, "me": who, "csrf": sess["csrf"] if sess else "", "flash": ctx.get("flash")},
            status_code=status,
        )

    async def require_csrf(request: Request) -> dict[str, str]:
        sess = session_of(request)
        if sess is None:
            raise PermissionError("Nicht angemeldet.")
        form = await request.form()
        if not secrets.compare_digest(str(form.get("csrf", "")), sess["csrf"]):
            raise PermissionError("Ungueltiges CSRF-Token.")
        request.state.form = form
        return sess

    # -- Anmeldung ------------------------------------------------------

    async def login_page(request: Request) -> HTMLResponse:
        if actor_of(request):
            return RedirectResponse("/", status_code=303)
        return render(request, "login.html", {"error": None})

    async def login(request: Request) -> Any:
        form = await request.form()
        participant = verifier.resolve(str(form.get("token", "")))
        if participant is None:
            return render(request, "login.html", {"error": "Token nicht erkannt."}, status=401)
        sid = sessions.create(participant.id)
        response = RedirectResponse("/", status_code=303)
        response.set_cookie(COOKIE, sid, httponly=True, samesite="strict", path="/")
        return response

    async def logout(request: Request) -> Any:
        sessions.drop(request.cookies.get(COOKIE))
        response = RedirectResponse("/login", status_code=303)
        response.delete_cookie(COOKIE, path="/")
        return response

    # -- Ansichten ------------------------------------------------------

    async def index(request: Request) -> Any:
        if not actor_of(request):
            return RedirectResponse("/login", status_code=303)
        return render(request, "index.html", {"threads": service.listing()})

    async def thread_page(request: Request) -> Any:
        actor = actor_of(request)
        if not actor:
            return RedirectResponse("/login", status_code=303)
        slug = request.path_params["slug"]
        try:
            data = service.read(actor, slug)
        except DialogError as exc:
            return render(request, "index.html", {"threads": service.listing(), "flash": str(exc)}, status=404)

        status = data["status"]
        my_probe_missing = (
            status["state"] == "probing"
            and actor in status["probers"]
            and actor in status["probes_missing"]
        )
        results = None
        if status["state"] != "probing":
            try:
                results = service.probe_results(actor, slug)
            except DialogError:
                results = None
        return render(request, "thread.html", {
            "status": status,
            "posts": data["posts"],
            # Blindheit: waehrend der Sondenphase liefert der Server die Sonden
            # gar nicht erst aus - im Markup verborgen waere keine Blindheit.
            "probes": data["probes"],
            "results": results,
            "my_probe_missing": my_probe_missing,
            "flash": request.query_params.get("flash"),
            "last_event": service.store.last_event_id(slug),
        })

    # -- Schreibende Routen ---------------------------------------------

    async def submit_probe(request: Request) -> Any:
        slug = request.path_params["slug"]
        try:
            sess = await require_csrf(request)
        except PermissionError as exc:
            return PlainTextResponse(str(exc), status_code=403)
        form = request.state.form
        evidence = _parse_evidence(str(form.get("evidence", "")))
        try:
            service.submit_probe(sess["participant"], slug, str(form.get("artifact", "")), evidence)
            flash = "Sonde eingereicht."
        except (DialogError, RuleViolation) as exc:
            flash = str(exc)
        return RedirectResponse(f"/t/{slug}?flash={flash}", status_code=303)

    def _owner_action(handler):
        async def route(request: Request) -> Any:
            slug = request.path_params["slug"]
            try:
                sess = await require_csrf(request)
            except PermissionError as exc:
                return PlainTextResponse(str(exc), status_code=403)
            who = service.store.participant(sess["participant"])
            if who is None or who.role != "owner":
                return PlainTextResponse(
                    "Diese Entscheidung ist dem Eigentuemer vorbehalten (debate-mode.md §4).",
                    status_code=403,
                )
            try:
                flash = handler(sess["participant"], slug, request.state.form)
            except (DialogError, RuleViolation) as exc:
                flash = str(exc)
            return RedirectResponse(f"/t/{slug}?flash={flash}", status_code=303)

        return route

    def _extend(actor: str, slug: str, form) -> str:
        rounds = int(form.get("extra_rounds") or 1)
        service.extend(actor, slug, rounds, str(form.get("reason", "")))
        return f"Um {rounds} Runde(n) verlaengert."

    def _repeat(actor: str, slug: str, form) -> str:
        service.repeat_probes(actor, slug, str(form.get("reason", "")))
        return "Sondenphase wird wiederholt."

    def _close(actor: str, slug: str, form) -> str:
        service.close(actor, slug, str(form.get("summary", "")))
        return "Thread geschlossen und exportiert."

    # -- Live-Aktualisierung --------------------------------------------

    async def events(request: Request) -> Any:
        if not actor_of(request):
            return PlainTextResponse("Nicht angemeldet.", status_code=403)
        slug = request.path_params["slug"]
        last = int(request.query_params.get("last", "0"))

        async def stream():
            nonlocal last
            while True:
                if await request.is_disconnected():
                    return
                for event in service.store.events_since(slug, last):
                    last = event["id"]
                    yield f"id: {event['id']}\ndata: {json.dumps(event)}\n\n"
                await asyncio.sleep(1.0)

        return StreamingResponse(
            stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
        )

    return [
        Route("/", index),
        Route("/login", login_page),
        Route("/login", login, methods=["POST"]),
        Route("/logout", logout, methods=["POST"]),
        Route("/t/{slug}", thread_page),
        Route("/t/{slug}/probe", submit_probe, methods=["POST"]),
        Route("/t/{slug}/extend", _owner_action(_extend), methods=["POST"]),
        Route("/t/{slug}/repeat-probes", _owner_action(_repeat), methods=["POST"]),
        Route("/t/{slug}/close", _owner_action(_close), methods=["POST"]),
        Route("/events/{slug}", events),
        Mount("/static", app=StaticFiles(directory=str(HERE / "static")), name="static"),
    ]


def _parse_evidence(raw: str) -> list[dict[str, str]]:
    """Eine Zeile je Fundstelle: `pfad — stelle` oder `pfad | stelle`."""
    out: list[dict[str, str]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        for sep in ("—", "|", "::"):
            if sep in line:
                path, locator = line.split(sep, 1)
                out.append({"path": path.strip(), "locator": locator.strip()})
                break
        else:
            out.append({"path": line, "locator": "-"})
    return out
