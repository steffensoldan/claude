"""Definition-of-Done item: cross-owner access to another user's job must
be rejected. This is the most likely real-world bug in a multi-tenant tool,
hence its own dedicated, explicit test file."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.auth import authenticate, create_user
from app.db import get_connection, init_db
from app.jobs import list_jobs_for_owner
from app.main import create_app


def _make_client_with_two_users(test_settings, fake_provider) -> TestClient:
    init_db(test_settings.database_path)
    conn = get_connection(test_settings.database_path)
    create_user(conn, "alice", "alice-pw")
    create_user(conn, "bob", "bob-pw")
    conn.close()

    app = create_app(test_settings, provider=fake_provider)
    return TestClient(app)


def test_cross_owner_download_is_rejected(test_settings, fake_provider):
    client = _make_client_with_two_users(test_settings, fake_provider)

    client.post("/login", data={"username": "alice", "password": "alice-pw"})
    client.post(
        "/jobs",
        data={"meeting_id": "meeting-1", "meeting_title": "Weekly Sync", "job_type": "translate"},
        follow_redirects=False,
    )
    conn = get_connection(test_settings.database_path)
    alice = authenticate(conn, "alice", "alice-pw")
    alice_job = list_jobs_for_owner(conn, alice.id)[0]
    conn.close()

    bob_client = TestClient(client.app)  # separate cookie jar
    bob_client.post("/login", data={"username": "bob", "password": "bob-pw"})

    status_response = bob_client.get(f"/jobs/{alice_job.id}")
    download_response = bob_client.get(f"/jobs/{alice_job.id}/download")

    assert status_response.status_code == 404
    assert download_response.status_code == 404


def test_cross_owner_job_list_is_isolated(test_settings, fake_provider):
    client = _make_client_with_two_users(test_settings, fake_provider)

    client.post("/login", data={"username": "alice", "password": "alice-pw"})
    client.post(
        "/jobs",
        data={"meeting_id": "meeting-1", "meeting_title": "Weekly Sync", "job_type": "translate"},
        follow_redirects=False,
    )

    conn = get_connection(test_settings.database_path)
    bob = authenticate(conn, "bob", "bob-pw")
    bob_jobs = list_jobs_for_owner(conn, bob.id)
    conn.close()

    assert bob_jobs == []
