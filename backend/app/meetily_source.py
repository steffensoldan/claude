"""Reads Meeting transcripts from Meetily's data store.

The concrete schema/format is a documented ASSUMPTION (see
../../docs/meetily-integration-spike.md) — no real Meetily installation was
available to verify it in this sandbox. Both implementations are isolated
behind the MeetilySource interface so only one class needs to change once
the real schema/format is confirmed on the target VM.
"""
from __future__ import annotations

import json
import sqlite3
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


class MeetilySourceError(Exception):
    """Raised when the configured Meetily data source cannot be read."""


@dataclass(frozen=True)
class Meeting:
    id: str
    title: str
    created_at: str
    transcript_text: str


class MeetilySource(ABC):
    @abstractmethod
    def list_meetings(self) -> list[Meeting]:
        """Return metadata for all available meetings (transcript text may
        be omitted/empty here; use get_transcript for the full text)."""

    @abstractmethod
    def get_transcript(self, meeting_id: str) -> str:
        """Return the full transcript text for one meeting."""


class SqliteMeetilySource(MeetilySource):
    """Verified against a real Meetily v0.4.0 installation (see
    ../../docs/meetily-integration-spike.md). `meetings(id, title, created_at,
    updated_at, folder_path)` holds metadata only — the transcript is NOT a
    column there. The actual text lives in `transcripts`, one row per audio
    segment (`meeting_id` is a plain foreign key, not unique), each with its
    own `transcript`, `speaker` ('mic'/'system'), and `audio_start_time`. The
    full meeting transcript is reassembled by concatenating all segment rows
    in chronological order. Opens the database read-only to avoid interfering
    with a live Meetily instance still writing to the same file."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        if not self._db_path.exists():
            raise MeetilySourceError(f"Meetily SQLite database not found: {self._db_path}")
        uri = f"file:{self._db_path}?mode=ro"
        try:
            return sqlite3.connect(uri, uri=True)
        except sqlite3.Error as exc:
            raise MeetilySourceError(f"Could not open Meetily database read-only: {exc}") from exc

    def list_meetings(self) -> list[Meeting]:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            try:
                rows = conn.execute(
                    "SELECT id, title, created_at FROM meetings ORDER BY created_at DESC"
                ).fetchall()
            except sqlite3.Error as exc:
                raise MeetilySourceError(f"Query against Meetily database failed: {exc}") from exc
        return [
            Meeting(id=row["id"], title=row["title"], created_at=row["created_at"], transcript_text="")
            for row in rows
        ]

    def get_transcript(self, meeting_id: str) -> str:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            try:
                meeting = conn.execute(
                    "SELECT id FROM meetings WHERE id = ?", (meeting_id,)
                ).fetchone()
                if meeting is None:
                    raise MeetilySourceError(f"No meeting found with id={meeting_id!r}")
                segments = conn.execute(
                    "SELECT transcript, speaker FROM transcripts WHERE meeting_id = ? "
                    "ORDER BY COALESCE(audio_start_time, 0), timestamp",
                    (meeting_id,),
                ).fetchall()
            except sqlite3.Error as exc:
                raise MeetilySourceError(f"Query against Meetily database failed: {exc}") from exc
        return "\n".join(
            f"{row['speaker']}: {row['transcript']}" if row["speaker"] else row["transcript"]
            for row in segments
        )


class ExportFolderMeetilySource(MeetilySource):
    """Assumed export format: one *.json file per meeting, see
    ../../docs/meetily-integration-spike.md. Preferred over SqliteMeetilySource
    since it decouples this project from Meetily's internal DB schema."""

    def __init__(self, folder_path: Path) -> None:
        self._folder_path = folder_path

    def _load_all(self) -> dict[str, Meeting]:
        if not self._folder_path.is_dir():
            raise MeetilySourceError(f"Meetily export folder not found: {self._folder_path}")

        meetings: dict[str, Meeting] = {}
        for export_file in sorted(self._folder_path.glob("*.json")):
            try:
                data = json.loads(export_file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise MeetilySourceError(f"Could not read export file {export_file}: {exc}") from exc

            try:
                meeting = Meeting(
                    id=data["id"],
                    title=data["title"],
                    created_at=data["created_at"],
                    transcript_text=data["transcript"],
                )
            except KeyError as exc:
                raise MeetilySourceError(
                    f"Export file {export_file} is missing expected field {exc}"
                ) from exc
            meetings[meeting.id] = meeting
        return meetings

    def list_meetings(self) -> list[Meeting]:
        meetings = self._load_all()
        return sorted(meetings.values(), key=lambda m: m.created_at, reverse=True)

    def get_transcript(self, meeting_id: str) -> str:
        meetings = self._load_all()
        if meeting_id not in meetings:
            raise MeetilySourceError(f"No meeting found with id={meeting_id!r}")
        return meetings[meeting_id].transcript_text


def get_meetily_source(mode: str, path: Path) -> MeetilySource:
    normalized = (mode or "").strip().lower()
    if normalized == "sqlite":
        return SqliteMeetilySource(path)
    if normalized == "export_folder":
        return ExportFolderMeetilySource(path)
    raise MeetilySourceError(
        f"Unknown MEETILY_SOURCE_MODE: {mode!r}. Expected 'sqlite' or 'export_folder'."
    )
