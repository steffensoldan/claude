"""SQLite schema and connection helper for users/sessions/jobs.

Deliberately separate from Meetily's own database (see meetily_source.py) —
this app never writes to Meetily's data store.
"""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from .config import load_settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash BLOB NOT NULL,
    salt BLOB NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    expires_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    owner_user_id INTEGER NOT NULL REFERENCES users(id),
    meeting_id TEXT NOT NULL,
    meeting_title TEXT NOT NULL,
    job_type TEXT NOT NULL,
    status TEXT NOT NULL,
    result_path TEXT,
    error_message TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def get_connection(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path) -> None:
    conn = get_connection(db_path)
    try:
        conn.executescript(_SCHEMA)
        conn.commit()
    finally:
        conn.close()


def _create_admin_user_if_requested(
    db_path: Path, username: str | None, password: str | None
) -> None:
    from .auth import create_user  # local import: avoids a circular import at module load time

    if not username or not password:
        print(
            "No ADMIN_USERNAME/ADMIN_PASSWORD set — skipping default user creation. "
            "Create one later via app.auth.create_user()."
        )
        return

    conn = get_connection(db_path)
    try:
        create_user(conn, username, password)
        print(f"Created admin user: {username}")
    finally:
        conn.close()


def _main() -> None:
    parser = argparse.ArgumentParser(description="Meetily-GLM-Bridge database management")
    parser.add_argument("command", choices=["init"])
    args = parser.parse_args()

    settings = load_settings()
    if args.command == "init":
        init_db(settings.database_path)
        print(f"Database initialized at {settings.database_path}")
        _create_admin_user_if_requested(
            settings.database_path, settings.admin_username, settings.admin_password
        )


if __name__ == "__main__":
    _main()
