"""FastAPI web interface — separate from Meetily's own admin panel.
Multi-user with login; lets a user start a translate/summarize job on a
Meetily transcript, poll its status, and download the result."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi import BackgroundTasks, Cookie, Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import auth, jobs
from .config import Settings, load_settings
from .db import get_connection, init_db
from .meetily_source import MeetilySource, MeetilySourceError, get_meetily_source
from .providers.base import TranslationProvider
from .providers.factory import get_provider

_BACKEND_DIR = Path(__file__).resolve().parents[1]
templates = Jinja2Templates(directory=str(_BACKEND_DIR / "templates"))


def _check_same_origin(request: Request) -> None:
    """Origin-check as a CSRF mitigation, alongside SameSite=Lax on the
    session cookie — a deliberately lighter alternative to a full
    CSRF-token framework (documented trade-off, see implementation_plan.md)."""
    origin = request.headers.get("origin")
    if origin is None:
        return  # same-origin browser form posts commonly omit Origin
    if origin != str(request.base_url).rstrip("/"):
        raise HTTPException(status_code=403, detail="Cross-origin request rejected")


def _run_job_in_background(
    job_id: str, settings: Settings, source: MeetilySource, provider: TranslationProvider
) -> None:
    """Uses its own DB connection, independent of the request-scoped one,
    since this runs after the HTTP response (and the request's connection
    dependency) has already been torn down."""
    conn = get_connection(settings.database_path)
    try:
        jobs.run_job(conn, job_id, source=source, provider=provider, download_dir=settings.download_dir)
    finally:
        conn.close()


def create_app(settings: Settings | None = None, *, provider: TranslationProvider | None = None) -> FastAPI:
    """`provider` can be injected directly (e.g. a test double) to bypass
    get_provider()'s real-SDK construction and PROVIDER env requirement."""
    settings = settings or load_settings()
    init_db(settings.database_path)

    app = FastAPI(title="Meetily-GLM-Bridge")
    app.state.settings = settings
    app.state.provider = provider or get_provider(settings)
    app.state.meetily_source = get_meetily_source(
        settings.meetily_source_mode, settings.meetily_source_path
    )
    app.mount("/static", StaticFiles(directory=str(_BACKEND_DIR / "static")), name="static")

    def get_db():
        conn = get_connection(settings.database_path)
        try:
            yield conn
        finally:
            conn.close()

    def get_current_user(
        session_token: str | None = Cookie(default=None),
        conn: sqlite3.Connection = Depends(get_db),
    ) -> auth.User | None:
        if session_token is None:
            return None
        return auth.get_user_for_session(conn, session_token)

    @app.get("/login", response_class=HTMLResponse)
    def login_page(request: Request):
        return templates.TemplateResponse(request=request, name="login.html", context={"error": None})

    @app.post("/login")
    def login_submit(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        conn: sqlite3.Connection = Depends(get_db),
    ):
        _check_same_origin(request)
        try:
            user = auth.authenticate(conn, username, password)
        except auth.AuthError:
            return templates.TemplateResponse(
                request=request,
                name="login.html",
                context={"error": "Ungültiger Benutzername oder Passwort"},
                status_code=401,
            )

        token = auth.create_session(conn, user.id)
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        # secure=False: app binds to 127.0.0.1 / VM-internal network without TLS by
        # default. If ever exposed beyond localhost, add TLS and set secure=True.
        response.set_cookie(
            "session_token", token, httponly=True, samesite="lax", secure=False, max_age=24 * 3600
        )
        return response

    @app.post("/logout")
    def logout(
        request: Request,
        session_token: str | None = Cookie(default=None),
        conn: sqlite3.Connection = Depends(get_db),
    ):
        _check_same_origin(request)
        if session_token:
            auth.delete_session(conn, session_token)
        response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        response.delete_cookie("session_token")
        return response

    @app.get("/", response_class=HTMLResponse)
    def dashboard(request: Request, user: auth.User | None = Depends(get_current_user), conn: sqlite3.Connection = Depends(get_db)):
        if user is None:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

        try:
            meetings = request.app.state.meetily_source.list_meetings()
        except MeetilySourceError:
            meetings = []

        user_jobs = jobs.list_jobs_for_owner(conn, user.id)
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={"user": user, "meetings": meetings, "jobs": user_jobs},
        )

    @app.post("/jobs")
    def create_job_route(
        request: Request,
        background_tasks: BackgroundTasks,
        meeting_id: str = Form(...),
        meeting_title: str = Form(...),
        job_type: str = Form(...),
        user: auth.User | None = Depends(get_current_user),
        conn: sqlite3.Connection = Depends(get_db),
    ):
        if user is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        _check_same_origin(request)

        try:
            job = jobs.create_job(conn, user.id, meeting_id, meeting_title, job_type)
        except jobs.JobError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        background_tasks.add_task(
            _run_job_in_background,
            job.id,
            request.app.state.settings,
            request.app.state.meetily_source,
            request.app.state.provider,
        )
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    @app.get("/jobs/{job_id}")
    def job_status(
        job_id: str,
        user: auth.User | None = Depends(get_current_user),
        conn: sqlite3.Connection = Depends(get_db),
    ):
        if user is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        try:
            job = jobs.get_job_for_owner(conn, job_id, user.id)
        except jobs.JobError as exc:
            raise HTTPException(status_code=404, detail="Job not found") from exc
        return {
            "id": job.id,
            "status": job.status,
            "job_type": job.job_type,
            "meeting_title": job.meeting_title,
            "error_message": job.error_message,
        }

    @app.get("/jobs/{job_id}/download")
    def job_download(
        job_id: str,
        user: auth.User | None = Depends(get_current_user),
        conn: sqlite3.Connection = Depends(get_db),
    ):
        if user is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        try:
            job = jobs.get_job_for_owner(conn, job_id, user.id)
        except jobs.JobError as exc:
            raise HTTPException(status_code=404, detail="Job not found") from exc

        if job.status != "done" or not job.result_path:
            raise HTTPException(status_code=409, detail="Job result not ready")

        return FileResponse(
            job.result_path,
            filename=f"{job.meeting_title}-{job.job_type}.txt",
            media_type="text/plain",
        )

    return app


# No eager `app = create_app()` at module scope on purpose: that would run
# get_provider()/load_settings() at import time and break importing this
# module without full env config (e.g. in tests). Run via uvicorn's factory
# mode instead: `uvicorn app.main:create_app --factory`.
