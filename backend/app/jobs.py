"""Job creation, status tracking, and execution. No task queue (Celery/RQ) —
jobs run via FastAPI BackgroundTasks, sufficient for a single-VM, low-volume
internal tool (Slim Code)."""
from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .meetily_source import MeetilySource
from .providers.base import TranslationProvider

_VALID_JOB_TYPES = {"translate", "summarize"}


class JobError(Exception):
    """Raised when a job cannot be found, or does not belong to the
    requesting user (both cases surface identically — see get_job_for_owner)."""


@dataclass(frozen=True)
class Job:
    id: str
    owner_user_id: int
    meeting_id: str
    meeting_title: str
    job_type: str
    status: str
    result_path: str | None
    error_message: str | None
    created_at: str
    updated_at: str


def create_job(
    conn: sqlite3.Connection,
    owner_user_id: int,
    meeting_id: str,
    meeting_title: str,
    job_type: str,
) -> Job:
    if job_type not in _VALID_JOB_TYPES:
        raise JobError(f"Unknown job_type: {job_type!r}")

    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT INTO jobs
            (id, owner_user_id, meeting_id, meeting_title, job_type, status,
             result_path, error_message, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, 'pending', NULL, NULL, ?, ?)
        """,
        (job_id, owner_user_id, meeting_id, meeting_title, job_type, now, now),
    )
    conn.commit()
    return get_job(conn, job_id)


def get_job(conn: sqlite3.Connection, job_id: str) -> Job:
    row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if row is None:
        raise JobError(f"No job found with id={job_id!r}")
    return _row_to_job(row)


def get_job_for_owner(conn: sqlite3.Connection, job_id: str, owner_user_id: int) -> Job:
    """Raises JobError if the job doesn't exist OR belongs to a different
    user — deliberately indistinguishable to the caller, so a download
    endpoint never reveals whether a foreign job ID exists."""
    job = get_job(conn, job_id)
    if job.owner_user_id != owner_user_id:
        raise JobError(f"No job found with id={job_id!r}")
    return job


def list_jobs_for_owner(conn: sqlite3.Connection, owner_user_id: int) -> list[Job]:
    rows = conn.execute(
        "SELECT * FROM jobs WHERE owner_user_id = ? ORDER BY created_at DESC",
        (owner_user_id,),
    ).fetchall()
    return [_row_to_job(row) for row in rows]


def _set_status(
    conn: sqlite3.Connection,
    job_id: str,
    status: str,
    *,
    result_path: str | None = None,
    error_message: str | None = None,
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE jobs SET status = ?, result_path = ?, error_message = ?, updated_at = ? WHERE id = ?",
        (status, result_path, error_message, now, job_id),
    )
    conn.commit()


def run_job(
    conn: sqlite3.Connection,
    job_id: str,
    *,
    source: MeetilySource,
    provider: TranslationProvider,
    download_dir: Path,
) -> None:
    """Executes a job synchronously. Intended to run inside a FastAPI
    BackgroundTask so the HTTP request returns immediately with status
    'pending'. Any failure (provider or Meetily-source related) is recorded
    as job status 'error' rather than left to crash silently in the
    background — this is the job runner's system boundary, so a broad
    except is intentional here."""
    job = get_job(conn, job_id)
    _set_status(conn, job_id, "running")

    try:
        transcript_text = source.get_transcript(job.meeting_id)
        if job.job_type == "translate":
            output_text = provider.translate(transcript_text).translated_text
        else:
            output_text = provider.summarize(transcript_text)

        download_dir.mkdir(parents=True, exist_ok=True)
        result_path = download_dir / f"{job_id}.txt"
        result_path.write_text(output_text, encoding="utf-8", newline="\n")
        _set_status(conn, job_id, "done", result_path=str(result_path))
    except Exception as exc:
        _set_status(conn, job_id, "error", error_message=str(exc))


def _row_to_job(row: sqlite3.Row) -> Job:
    return Job(
        id=row["id"],
        owner_user_id=row["owner_user_id"],
        meeting_id=row["meeting_id"],
        meeting_title=row["meeting_title"],
        job_type=row["job_type"],
        status=row["status"],
        result_path=row["result_path"],
        error_message=row["error_message"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
