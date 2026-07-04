from __future__ import annotations

from fastapi.testclient import TestClient

from app.auth import authenticate, create_user
from app.db import get_connection, init_db
from app.jobs import list_jobs_for_owner
from app.main import create_app


def _make_client(test_settings, fake_provider) -> TestClient:
    init_db(test_settings.database_path)
    conn = get_connection(test_settings.database_path)
    create_user(conn, "alice", "alice-password")
    conn.close()

    app = create_app(test_settings, provider=fake_provider)
    return TestClient(app)


def _login(client: TestClient, username: str = "alice", password: str = "alice-password"):
    return client.post(
        "/login", data={"username": username, "password": password}, follow_redirects=False
    )


def test_login_success_sets_cookie_and_redirects(test_settings, fake_provider):
    client = _make_client(test_settings, fake_provider)

    response = _login(client)

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert "session_token" in response.cookies


def test_login_failure_shows_error(test_settings, fake_provider):
    client = _make_client(test_settings, fake_provider)

    response = client.post("/login", data={"username": "alice", "password": "wrong"})

    assert response.status_code == 401
    assert "Ungültiger" in response.text


def test_dashboard_requires_login(test_settings, fake_provider):
    client = _make_client(test_settings, fake_provider)

    response = client.get("/", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_dashboard_shows_meetings_after_login(test_settings, fake_provider):
    client = _make_client(test_settings, fake_provider)
    _login(client)

    response = client.get("/")

    assert response.status_code == 200
    assert "Weekly Sync" in response.text


def test_create_job_requires_login(test_settings, fake_provider):
    client = _make_client(test_settings, fake_provider)

    response = client.post(
        "/jobs",
        data={"meeting_id": "meeting-1", "meeting_title": "Weekly Sync", "job_type": "translate"},
    )

    assert response.status_code == 401


def test_create_job_runs_and_completes_synchronously(test_settings, fake_provider):
    client = _make_client(test_settings, fake_provider)
    _login(client)

    response = client.post(
        "/jobs",
        data={"meeting_id": "meeting-1", "meeting_title": "Weekly Sync", "job_type": "translate"},
        follow_redirects=False,
    )
    assert response.status_code == 303

    conn = get_connection(test_settings.database_path)
    user = authenticate(conn, "alice", "alice-password")
    finished_jobs = list_jobs_for_owner(conn, user.id)
    conn.close()

    assert len(finished_jobs) == 1
    assert finished_jobs[0].status == "done"


def _create_and_finish_job(client: TestClient, test_settings, job_type: str = "translate"):
    client.post(
        "/jobs",
        data={"meeting_id": "meeting-1", "meeting_title": "Weekly Sync", "job_type": job_type},
        follow_redirects=False,
    )
    conn = get_connection(test_settings.database_path)
    user = authenticate(conn, "alice", "alice-password")
    job = list_jobs_for_owner(conn, user.id)[0]
    conn.close()
    return job


def test_job_status_endpoint_returns_json(test_settings, fake_provider):
    client = _make_client(test_settings, fake_provider)
    _login(client)
    job = _create_and_finish_job(client, test_settings)

    response = client.get(f"/jobs/{job.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "done"
    assert body["job_type"] == "translate"


def test_download_returns_translated_content(test_settings, fake_provider):
    client = _make_client(test_settings, fake_provider)
    _login(client)
    job = _create_and_finish_job(client, test_settings)

    response = client.get(f"/jobs/{job.id}/download")

    assert response.status_code == 200
    assert "[de]" in response.text
    assert "Speaker 1" in response.text


def test_status_endpoint_requires_login(test_settings, fake_provider):
    client = _make_client(test_settings, fake_provider)
    _login(client)
    job = _create_and_finish_job(client, test_settings)

    anon_client = TestClient(client.app)  # fresh client -> no session cookie
    response = anon_client.get(f"/jobs/{job.id}")

    assert response.status_code == 401


def test_download_not_ready_returns_409_for_pending_job(test_settings, fake_provider):
    client = _make_client(test_settings, fake_provider)
    _login(client)

    conn = get_connection(test_settings.database_path)
    user = authenticate(conn, "alice", "alice-password")
    from app.jobs import create_job

    job = create_job(conn, user.id, "meeting-1", "Weekly Sync", "translate")
    conn.close()

    response = client.get(f"/jobs/{job.id}/download")

    assert response.status_code == 409
