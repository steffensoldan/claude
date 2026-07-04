from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.meetily_source import (
    ExportFolderMeetilySource,
    MeetilySourceError,
    SqliteMeetilySource,
    get_meetily_source,
)


def test_export_folder_source_lists_and_reads(meetily_export_dir):
    source = ExportFolderMeetilySource(meetily_export_dir)

    meetings = source.list_meetings()

    assert len(meetings) == 1
    assert meetings[0].id == "meeting-1"
    assert "Speaker 1" in source.get_transcript("meeting-1")


def test_export_folder_source_unknown_meeting_raises(meetily_export_dir):
    source = ExportFolderMeetilySource(meetily_export_dir)

    with pytest.raises(MeetilySourceError):
        source.get_transcript("does-not-exist")


def test_export_folder_source_missing_folder_raises(tmp_path):
    source = ExportFolderMeetilySource(tmp_path / "missing")

    with pytest.raises(MeetilySourceError):
        source.list_meetings()


def test_export_folder_source_malformed_json_raises(tmp_path):
    export_dir = tmp_path / "exports"
    export_dir.mkdir()
    (export_dir / "broken.json").write_text("{not valid json", encoding="utf-8")
    source = ExportFolderMeetilySource(export_dir)

    with pytest.raises(MeetilySourceError):
        source.list_meetings()


def test_export_folder_source_missing_field_raises(tmp_path):
    import json

    export_dir = tmp_path / "exports"
    export_dir.mkdir()
    (export_dir / "incomplete.json").write_text(json.dumps({"id": "x"}), encoding="utf-8")
    source = ExportFolderMeetilySource(export_dir)

    with pytest.raises(MeetilySourceError):
        source.list_meetings()


def _make_sqlite_fixture(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE meetings (id TEXT PRIMARY KEY, title TEXT, created_at TEXT, transcript_text TEXT)"
    )
    conn.execute(
        "INSERT INTO meetings VALUES (?, ?, ?, ?)",
        ("m1", "Sync", "2026-07-01T10:00:00+00:00", "Hello world"),
    )
    conn.commit()
    conn.close()


def test_sqlite_source_lists_and_reads(tmp_path):
    db_path = tmp_path / "meetily.db"
    _make_sqlite_fixture(db_path)
    source = SqliteMeetilySource(db_path)

    meetings = source.list_meetings()

    assert len(meetings) == 1
    assert meetings[0].id == "m1"
    assert source.get_transcript("m1") == "Hello world"


def test_sqlite_source_missing_file_raises(tmp_path):
    source = SqliteMeetilySource(tmp_path / "missing.db")

    with pytest.raises(MeetilySourceError):
        source.list_meetings()


def test_sqlite_source_unknown_meeting_raises(tmp_path):
    db_path = tmp_path / "meetily.db"
    _make_sqlite_fixture(db_path)
    source = SqliteMeetilySource(db_path)

    with pytest.raises(MeetilySourceError):
        source.get_transcript("does-not-exist")


def test_get_meetily_source_factory_export_folder(tmp_path):
    assert isinstance(get_meetily_source("export_folder", tmp_path), ExportFolderMeetilySource)


def test_get_meetily_source_factory_sqlite(tmp_path):
    assert isinstance(get_meetily_source("sqlite", tmp_path / "x.db"), SqliteMeetilySource)


def test_get_meetily_source_factory_unknown_mode_raises(tmp_path):
    with pytest.raises(MeetilySourceError):
        get_meetily_source("bogus", tmp_path)
