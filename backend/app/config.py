"""Runtime configuration loaded from environment variables.

No hardcoded absolute paths or secrets — everything portable and overridable
via .env. See ../../.env.example for the full list of recognized variables.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    provider: str
    anthropic_api_key: str | None
    anthropic_model: str
    scaleway_api_key: str | None
    scaleway_model: str
    scaleway_base_url: str
    database_path: Path
    download_dir: Path
    meetily_source_mode: str
    meetily_source_path: Path
    admin_username: str | None
    admin_password: str | None
    host: str
    port: int


def _resolve_path(raw: str | None, default: Path) -> Path:
    """Relative paths (whether from .env or the default) are resolved against
    the project root, not the process's current working directory — the
    documented setup runs uvicorn from backend/, which would otherwise
    silently write data next to the wrong directory."""
    path = Path(raw) if raw else default
    return path if path.is_absolute() else (_PROJECT_ROOT / path).resolve()


def load_settings() -> Settings:
    data_dir = Path("data")
    return Settings(
        provider=os.environ.get("PROVIDER", "anthropic"),
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
        anthropic_model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5"),
        scaleway_api_key=os.environ.get("SCALEWAY_API_KEY"),
        scaleway_model=os.environ.get("SCALEWAY_MODEL", "glm-5.2"),
        scaleway_base_url=os.environ.get("SCALEWAY_BASE_URL", "https://api.scaleway.ai/v1"),
        database_path=_resolve_path(os.environ.get("DATABASE_PATH"), data_dir / "app.db"),
        download_dir=_resolve_path(os.environ.get("DOWNLOAD_DIR"), data_dir / "downloads"),
        meetily_source_mode=os.environ.get("MEETILY_SOURCE_MODE", "export_folder"),
        meetily_source_path=_resolve_path(
            os.environ.get("MEETILY_SOURCE_PATH"), data_dir / "meetily_exports"
        ),
        admin_username=os.environ.get("ADMIN_USERNAME"),
        admin_password=os.environ.get("ADMIN_PASSWORD"),
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8000")),
    )
