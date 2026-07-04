from __future__ import annotations

import pytest

from app import auth
from app.db import get_connection, init_db


@pytest.fixture
def conn(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    connection = get_connection(db_path)
    yield connection
    connection.close()


def test_create_and_authenticate_user(conn):
    auth.create_user(conn, "alice", "correct horse battery staple")

    user = auth.authenticate(conn, "alice", "correct horse battery staple")

    assert user.username == "alice"


def test_authenticate_wrong_password_raises(conn):
    auth.create_user(conn, "alice", "correct-password")

    with pytest.raises(auth.AuthError):
        auth.authenticate(conn, "alice", "wrong-password")


def test_authenticate_unknown_user_raises(conn):
    with pytest.raises(auth.AuthError):
        auth.authenticate(conn, "nobody", "whatever")


def test_create_duplicate_username_raises(conn):
    auth.create_user(conn, "alice", "pw1")

    with pytest.raises(auth.AuthError):
        auth.create_user(conn, "alice", "pw2")


def test_session_roundtrip(conn):
    user = auth.create_user(conn, "alice", "pw")
    token = auth.create_session(conn, user.id)

    resolved = auth.get_user_for_session(conn, token)

    assert resolved is not None
    assert resolved.username == "alice"


def test_unknown_session_token_returns_none(conn):
    assert auth.get_user_for_session(conn, "does-not-exist") is None


def test_expired_session_returns_none(conn):
    user = auth.create_user(conn, "alice", "pw")
    token = auth.create_session(conn, user.id, ttl_hours=-1)

    assert auth.get_user_for_session(conn, token) is None


def test_delete_session_invalidates_it(conn):
    user = auth.create_user(conn, "alice", "pw")
    token = auth.create_session(conn, user.id)

    auth.delete_session(conn, token)

    assert auth.get_user_for_session(conn, token) is None
