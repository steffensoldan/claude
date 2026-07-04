"""End-to-end: synthetic Meetily export fixture -> job -> (mocked) provider
-> download, with content comparison."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.auth import authenticate, create_user
from app.db import get_connection, init_db
from app.jobs import list_jobs_for_owner
from app.main import create_app


def test_full_pipeline_transcript_to_download(test_settings, fake_provider):
    init_db(test_settings.database_path)
    conn = get_connection(test_settings.database_path)
    create_user(conn, "alice", "alice-pw")
    conn.close()

    app = create_app(test_settings, provider=fake_provider)
    client = TestClient(app)

    client.post("/login", data={"username": "alice", "password": "alice-pw"})

    dashboard_before = client.get("/")
    assert "Weekly Sync" in dashboard_before.text

    client.post(
        "/jobs",
        data={"meeting_id": "meeting-1", "meeting_title": "Weekly Sync", "job_type": "translate"},
        follow_redirects=False,
    )

    conn = get_connection(test_settings.database_path)
    user = authenticate(conn, "alice", "alice-pw")
    translate_job = list_jobs_for_owner(conn, user.id)[0]
    conn.close()

    assert translate_job.status == "done"

    download = client.get(f"/jobs/{translate_job.id}/download")
    assert download.status_code == 200
    assert download.text == "[de] Speaker 1: Hello.\nSpeaker 2: Hi there."

    # Follow-on summary of the same meeting — "optional Zusammenfassung
    # erstellen", separate from Meetily's own admin panel.
    client.post(
        "/jobs",
        data={"meeting_id": "meeting-1", "meeting_title": "Weekly Sync", "job_type": "summarize"},
        follow_redirects=False,
    )

    conn = get_connection(test_settings.database_path)
    all_jobs = list_jobs_for_owner(conn, user.id)
    conn.close()

    summarize_job = next(job for job in all_jobs if job.job_type == "summarize")
    assert summarize_job.status == "done"

    summary_download = client.get(f"/jobs/{summarize_job.id}/download")
    assert summary_download.text.startswith("[summary-de]")
