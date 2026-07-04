"""Password hashing (stdlib scrypt, no extra dependency) and server-side
session tokens (opaque random string, stored in the sessions table —
no signing secret needed)."""
from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1
_KEY_LEN = 64
_SESSION_TOKEN_BYTES = 32
_DEFAULT_SESSION_TTL_HOURS = 24


class AuthError(Exception):
    """Raised on invalid credentials, duplicate usernames, or expired/unknown sessions."""


@dataclass(frozen=True)
class User:
    id: int
    username: str


def hash_password(password: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
    salt = salt if salt is not None else os.urandom(16)
    derived = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P, dklen=_KEY_LEN
    )
    return derived, salt


def verify_password(password: str, password_hash: bytes, salt: bytes) -> bool:
    candidate, _ = hash_password(password, salt=salt)
    return hmac.compare_digest(candidate, password_hash)


def create_user(conn: sqlite3.Connection, username: str, password: str) -> User:
    existing = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if existing is not None:
        raise AuthError(f"Username already exists: {username!r}")

    password_hash, salt = hash_password(password)
    now = datetime.now(timezone.utc).isoformat()
    cursor = conn.execute(
        "INSERT INTO users (username, password_hash, salt, created_at) VALUES (?, ?, ?, ?)",
        (username, password_hash, salt, now),
    )
    conn.commit()
    return User(id=cursor.lastrowid, username=username)


def authenticate(conn: sqlite3.Connection, username: str, password: str) -> User:
    row = conn.execute(
        "SELECT id, username, password_hash, salt FROM users WHERE username = ?", (username,)
    ).fetchone()
    if row is None or not verify_password(password, row["password_hash"], row["salt"]):
        raise AuthError("Invalid username or password")
    return User(id=row["id"], username=row["username"])


def create_session(
    conn: sqlite3.Connection, user_id: int, ttl_hours: int = _DEFAULT_SESSION_TTL_HOURS
) -> str:
    token = secrets.token_urlsafe(_SESSION_TOKEN_BYTES)
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=ttl_hours)).isoformat()
    conn.execute(
        "INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)",
        (token, user_id, expires_at),
    )
    conn.commit()
    return token


def get_user_for_session(conn: sqlite3.Connection, token: str) -> User | None:
    row = conn.execute(
        """
        SELECT sessions.expires_at, users.id, users.username
        FROM sessions JOIN users ON users.id = sessions.user_id
        WHERE sessions.token = ?
        """,
        (token,),
    ).fetchone()
    if row is None:
        return None

    expires_at = datetime.fromisoformat(row["expires_at"])
    if expires_at < datetime.now(timezone.utc):
        delete_session(conn, token)
        return None
    return User(id=row["id"], username=row["username"])


def delete_session(conn: sqlite3.Connection, token: str) -> None:
    conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
