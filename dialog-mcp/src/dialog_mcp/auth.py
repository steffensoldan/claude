"""Konfiguration und Identitaet.

Wer ein Aufrufer ist, steht ausschliesslich im Bearer-Token. Kein Werkzeug
nimmt eine Teilnehmer-ID als Argument entgegen - sonst koennte sich ein Agent
als der andere ausgeben und ausser der Reihe schreiben.
"""

from __future__ import annotations

import hashlib
import secrets
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from mcp.server.auth.provider import AccessToken

ROLES = ("owner", "debater", "prober")


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@dataclass
class ParticipantConfig:
    id: str
    display_name: str
    role: str
    token: str
    human: bool = False


@dataclass
class Config:
    host: str = "127.0.0.1"
    port: int = 8770
    database: str = "dialog.sqlite3"
    export_dir: str | None = None
    public_url: str = "http://127.0.0.1:8770"
    participants: list[ParticipantConfig] = field(default_factory=list)

    @classmethod
    def load(cls, path: str | Path) -> "Config":
        raw = tomllib.loads(Path(path).read_text(encoding="utf-8"))
        server = raw.get("server", {})
        participants = []
        for entry in raw.get("participants", []):
            missing = [k for k in ("id", "token") if not entry.get(k)]
            if missing:
                raise ValueError(f"Teilnehmer ohne {', '.join(missing)} in {path}")
            role = entry.get("role", "debater")
            if role not in ROLES:
                raise ValueError(f"Unbekannte Rolle {role!r} fuer {entry['id']!r}. Zulaessig: {', '.join(ROLES)}.")
            participants.append(
                ParticipantConfig(
                    id=entry["id"],
                    display_name=entry.get("display_name", entry["id"]),
                    role=role,
                    token=entry["token"],
                    human=bool(entry.get("human", False)),
                )
            )
        if not participants:
            raise ValueError(f"{path} enthaelt keine Teilnehmer.")
        seen_tokens = {p.token for p in participants}
        if len(seen_tokens) != len(participants):
            raise ValueError("Zwei Teilnehmer teilen sich ein Token - Identitaeten waeren nicht unterscheidbar.")
        return cls(
            host=server.get("host", "127.0.0.1"),
            port=int(server.get("port", 8770)),
            database=server.get("database", "dialog.sqlite3"),
            export_dir=server.get("export_dir"),
            public_url=server.get("public_url", "http://127.0.0.1:8770"),
            participants=participants,
        )


class StaticTokenVerifier:
    """Bearer-Token aus der Konfiguration -> Teilnehmer.

    Vergleich ueber `secrets.compare_digest` auf dem Hash, damit die Laufzeit
    nicht verraet, wie weit ein geratenes Token gepasst hat.
    """

    def __init__(self, participants: list[ParticipantConfig]) -> None:
        self._by_hash = {token_hash(p.token): p for p in participants}

    async def verify_token(self, token: str) -> AccessToken | None:
        candidate = token_hash(token)
        for known, participant in self._by_hash.items():
            if secrets.compare_digest(candidate, known):
                return AccessToken(
                    token=token,
                    client_id=participant.id,
                    scopes=["dialog"],
                    subject=participant.id,
                )
        return None

    def resolve(self, token: str) -> ParticipantConfig | None:
        candidate = token_hash(token)
        for known, participant in self._by_hash.items():
            if secrets.compare_digest(candidate, known):
                return participant
        return None
