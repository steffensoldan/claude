from __future__ import annotations

from pathlib import Path

import pytest

from app import jobs
from app.auth import create_user
from app.db import get_connection, init_db
from app.meetily_source import ExportFolderMeetilySource


@pytest.fixture
def conn(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    connection = get_connection(db_path)
    yield connection
    connection.close()


@pytest.fixture
def user_id(conn) -> int:
    return create_user(conn, "alice", "pw").id


def test_create_job_defaults_to_pending(conn, user_id):
    job = jobs.create_job(conn, user_id, "m1", "Sync", "translate")

    assert job.status == "pending"
    assert job.owner_user_id == user_id


def test_create_job_rejects_unknown_job_type(conn, user_id):
    with pytest.raises(jobs.JobError):
        jobs.create_job(conn, user_id, "m1", "Sync", "bogus")


def test_get_job_for_owner_rejects_foreign_owner(conn, user_id):
    other_user = create_user(conn, "bob", "pw")
    job = jobs.create_job(conn, user_id, "m1", "Sync", "translate")

    with pytest.raises(jobs.JobError):
        jobs.get_job_for_owner(conn, job.id, other_user.id)


def test_get_job_for_owner_succeeds_for_actual_owner(conn, user_id):
    job = jobs.create_job(conn, user_id, "m1", "Sync", "translate")

    resolved = jobs.get_job_for_owner(conn, job.id, user_id)

    assert resolved.id == job.id


def test_list_jobs_for_owner_only_returns_own_jobs(conn, user_id):
    other_user = create_user(conn, "bob", "pw")
    jobs.create_job(conn, user_id, "m1", "Sync", "translate")
    jobs.create_job(conn, other_user.id, "m2", "Other", "translate")

    own_jobs = jobs.list_jobs_for_owner(conn, user_id)

    assert len(own_jobs) == 1
    assert own_jobs[0].meeting_id == "m1"


def test_run_job_translate_success(conn, user_id, tmp_path, meetily_export_dir, fake_provider):
    job = jobs.create_job(conn, user_id, "meeting-1", "Weekly Sync", "translate")
    source = ExportFolderMeetilySource(meetily_export_dir)

    jobs.run_job(conn, job.id, source=source, provider=fake_provider, download_dir=tmp_path / "downloads")

    finished = jobs.get_job(conn, job.id)
    assert finished.status == "done"
    assert finished.result_path is not None
    assert Path(finished.result_path).exists()
    assert fake_provider.translate_calls == ["Speaker 1: Hello.\nSpeaker 2: Hi there."]


def test_run_job_summarize_success(conn, user_id, tmp_path, meetily_export_dir, fake_provider):
    job = jobs.create_job(conn, user_id, "meeting-1", "Weekly Sync", "summarize")
    source = ExportFolderMeetilySource(meetily_export_dir)

    jobs.run_job(conn, job.id, source=source, provider=fake_provider, download_dir=tmp_path / "downloads")

    finished = jobs.get_job(conn, job.id)
    assert finished.status == "done"
    assert len(fake_provider.summarize_calls) == 1


def test_run_job_records_error_on_missing_meeting(conn, user_id, tmp_path, meetily_export_dir, fake_provider):
    job = jobs.create_job(conn, user_id, "does-not-exist", "Ghost", "translate")
    source = ExportFolderMeetilySource(meetily_export_dir)

    jobs.run_job(conn, job.id, source=source, provider=fake_provider, download_dir=tmp_path / "downloads")

    finished = jobs.get_job(conn, job.id)
    assert finished.status == "error"
    assert finished.error_message is not None
