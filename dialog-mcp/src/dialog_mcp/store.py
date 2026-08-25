"""SQLite-Ablage: Threads, Teilnehmer, Sonden, Beitraege, Ereignisse.

Die Datenbank ist die Wahrheit ueber einen laufenden Dialog. Das AOS-Markdown
entsteht erst beim Abschluss (`export.py`) und ist Nachweis, nicht Quelle.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS participants (
    id            TEXT PRIMARY KEY,
    display_name  TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('owner', 'debater', 'prober')),
    token_sha256  TEXT NOT NULL UNIQUE,
    is_human      INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS threads (
    slug         TEXT PRIMARY KEY,
    topic        TEXT NOT NULL,
    profile      TEXT NOT NULL CHECK (profile IN ('strict', 'light')),
    state        TEXT NOT NULL CHECK (state IN ('probing', 'probe_review', 'debating', 'done')),
    debaters     TEXT NOT NULL,
    probers      TEXT NOT NULL,
    turn         TEXT,
    round        INTEGER NOT NULL DEFAULT 1,
    max_rounds   INTEGER NOT NULL,
    probe_round  INTEGER NOT NULL DEFAULT 1,
    opened_by    TEXT NOT NULL,
    outcome      TEXT,
    summary      TEXT,
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL,
    closed_at    TEXT
);

CREATE TABLE IF NOT EXISTS probes (
    slug         TEXT NOT NULL REFERENCES threads(slug) ON DELETE CASCADE,
    participant  TEXT NOT NULL,
    probe_round  INTEGER NOT NULL,
    artifact     TEXT NOT NULL,
    evidence     TEXT NOT NULL,
    is_human     INTEGER NOT NULL DEFAULT 0,
    created_at   TEXT NOT NULL,
    PRIMARY KEY (slug, participant, probe_round)
);

CREATE TABLE IF NOT EXISTS posts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    slug         TEXT NOT NULL REFERENCES threads(slug) ON DELETE CASCADE,
    participant  TEXT NOT NULL,
    round        INTEGER NOT NULL,
    body         TEXT NOT NULL,
    evidence     TEXT NOT NULL,
    objections   TEXT NOT NULL,
    clearances   TEXT NOT NULL,
    priorities   TEXT,
    matrix       TEXT,
    residual     TEXT,
    extension    TEXT,
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    slug        TEXT NOT NULL,
    kind        TEXT NOT NULL,
    actor       TEXT NOT NULL,
    detail      TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_posts_slug ON posts(slug, round, id);
CREATE INDEX IF NOT EXISTS idx_events_slug ON events(slug, id);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class Participant:
    id: str
    display_name: str
    role: str
    is_human: bool


class Store:
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path, check_same_thread=False, isolation_level=None)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)

    # -- Teilnehmer -----------------------------------------------------

    def upsert_participant(
        self, pid: str, display_name: str, role: str, token_sha256: str, is_human: bool = False
    ) -> None:
        self._conn.execute(
            "INSERT INTO participants (id, display_name, role, token_sha256, is_human) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET display_name=excluded.display_name, "
            "role=excluded.role, token_sha256=excluded.token_sha256, is_human=excluded.is_human",
            (pid, display_name, role, token_sha256, int(is_human)),
        )

    def participant(self, pid: str) -> Participant | None:
        row = self._conn.execute("SELECT * FROM participants WHERE id = ?", (pid,)).fetchone()
        return self._participant(row) if row else None

    def participant_by_token_hash(self, token_sha256: str) -> Participant | None:
        row = self._conn.execute(
            "SELECT * FROM participants WHERE token_sha256 = ?", (token_sha256,)
        ).fetchone()
        return self._participant(row) if row else None

    def participants(self) -> list[Participant]:
        rows = self._conn.execute("SELECT * FROM participants ORDER BY id").fetchall()
        return [self._participant(r) for r in rows]

    @staticmethod
    def _participant(row: sqlite3.Row) -> Participant:
        return Participant(row["id"], row["display_name"], row["role"], bool(row["is_human"]))

    # -- Threads --------------------------------------------------------

    def create_thread(
        self,
        *,
        slug: str,
        topic: str,
        profile: str,
        debaters: list[str],
        probers: list[str],
        max_rounds: int,
        opened_by: str,
    ) -> dict[str, Any]:
        ts = now()
        self._conn.execute(
            "INSERT INTO threads (slug, topic, profile, state, debaters, probers, turn, round, "
            "max_rounds, probe_round, opened_by, created_at, updated_at) "
            "VALUES (?, ?, ?, 'probing', ?, ?, NULL, 1, ?, 1, ?, ?, ?)",
            (slug, topic, profile, json.dumps(debaters), json.dumps(probers), max_rounds, opened_by, ts, ts),
        )
        return self.thread(slug)  # type: ignore[return-value]

    def thread(self, slug: str) -> dict[str, Any] | None:
        row = self._conn.execute("SELECT * FROM threads WHERE slug = ?", (slug,)).fetchone()
        if row is None:
            return None
        t = dict(row)
        t["debaters"] = json.loads(t["debaters"])
        t["probers"] = json.loads(t["probers"])
        return t

    def threads(self, state: str | None = None) -> list[dict[str, Any]]:
        if state:
            rows = self._conn.execute(
                "SELECT slug FROM threads WHERE state = ? ORDER BY updated_at DESC", (state,)
            ).fetchall()
        else:
            rows = self._conn.execute("SELECT slug FROM threads ORDER BY updated_at DESC").fetchall()
        return [self.thread(r["slug"]) for r in rows]  # type: ignore[misc]

    def update_thread(self, slug: str, **fields: Any) -> None:
        if not fields:
            return
        fields["updated_at"] = now()
        assignments = ", ".join(f'"{k}" = ?' for k in fields)
        self._conn.execute(
            f"UPDATE threads SET {assignments} WHERE slug = ?", (*fields.values(), slug)
        )

    # -- Sonden ---------------------------------------------------------

    def add_probe(
        self, slug: str, participant: str, probe_round: int, artifact: str,
        evidence: list[dict[str, str]], is_human: bool,
    ) -> None:
        self._conn.execute(
            "INSERT INTO probes (slug, participant, probe_round, artifact, evidence, is_human, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (slug, participant, probe_round, artifact, json.dumps(evidence), int(is_human), now()),
        )

    def probes(self, slug: str, probe_round: int) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM probes WHERE slug = ? AND probe_round = ? ORDER BY created_at, participant",
            (slug, probe_round),
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["evidence"] = json.loads(d["evidence"])
            d["is_human"] = bool(d["is_human"])
            out.append(d)
        return out

    def all_probes(self, slug: str) -> list[dict[str, Any]]:
        rounds = self._conn.execute(
            "SELECT DISTINCT probe_round FROM probes WHERE slug = ? ORDER BY probe_round", (slug,)
        ).fetchall()
        return [p for r in rounds for p in self.probes(slug, r["probe_round"])]

    # -- Beitraege ------------------------------------------------------

    def add_post(self, slug: str, participant: str, round_no: int, payload: dict[str, Any]) -> int:
        cur = self._conn.execute(
            "INSERT INTO posts (slug, participant, round, body, evidence, objections, clearances, "
            "priorities, matrix, residual, extension, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                slug, participant, round_no,
                payload["body"],
                json.dumps(payload.get("evidence") or []),
                json.dumps(payload.get("objections") or []),
                json.dumps(payload.get("clearances") or []),
                json.dumps(payload.get("priorities")) if payload.get("priorities") else None,
                json.dumps(payload.get("matrix")) if payload.get("matrix") else None,
                json.dumps(payload.get("residual")) if payload.get("residual") else None,
                payload.get("extension") or None,
                now(),
            ),
        )
        return int(cur.lastrowid)

    def posts(self, slug: str, since_round: int = 0) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM posts WHERE slug = ? AND round >= ? ORDER BY id", (slug, since_round)
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            for key in ("evidence", "objections", "clearances", "priorities", "matrix", "residual"):
                d[key] = json.loads(d[key]) if d[key] else ([] if key in ("evidence", "objections", "clearances") else None)
            out.append(d)
        return out

    def posts_in_round(self, slug: str, round_no: int) -> list[dict[str, Any]]:
        return [p for p in self.posts(slug) if p["round"] == round_no]

    # -- Ereignisse -----------------------------------------------------

    def add_event(self, slug: str, kind: str, actor: str, detail: str = "") -> int:
        cur = self._conn.execute(
            "INSERT INTO events (slug, kind, actor, detail, created_at) VALUES (?, ?, ?, ?, ?)",
            (slug, kind, actor, detail, now()),
        )
        return int(cur.lastrowid)

    def events_since(self, slug: str, last_id: int) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM events WHERE slug = ? AND id > ? ORDER BY id", (slug, last_id)
        ).fetchall()
        return [dict(r) for r in rows]

    def last_event_id(self, slug: str) -> int:
        row = self._conn.execute("SELECT COALESCE(MAX(id), 0) AS m FROM events WHERE slug = ?", (slug,)).fetchone()
        return int(row["m"])

    def close(self) -> None:
        self._conn.close()
