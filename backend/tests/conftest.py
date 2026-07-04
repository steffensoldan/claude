from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.config import Settings
from app.providers.base import TranslationProvider, TranslationResult


class FakeProvider(TranslationProvider):
    """Deterministic stand-in for a real LLM provider. Used throughout the
    test suite so the autonomous test loop never depends on network access,
    API cost, or non-determinism."""

    def __init__(self) -> None:
        self.translate_calls: list[str] = []
        self.summarize_calls: list[str] = []

    def translate(self, transcript_text: str, *, target_language: str = "de") -> TranslationResult:
        self.translate_calls.append(transcript_text)
        return TranslationResult(
            translated_text=f"[{target_language}] {transcript_text}",
            model_used="fake-model",
        )

    def summarize(self, transcript_text: str, *, language: str = "de") -> str:
        self.summarize_calls.append(transcript_text)
        return f"[summary-{language}] {transcript_text[:20]}"


@pytest.fixture
def fake_provider() -> FakeProvider:
    return FakeProvider()


@pytest.fixture
def meetily_export_dir(tmp_path: Path) -> Path:
    export_dir = tmp_path / "meetily_exports"
    export_dir.mkdir()
    meeting = {
        "id": "meeting-1",
        "title": "Weekly Sync",
        "created_at": "2026-07-01T10:00:00+00:00",
        "transcript": "Speaker 1: Hello.\nSpeaker 2: Hi there.",
    }
    (export_dir / "meeting-1.json").write_text(json.dumps(meeting), encoding="utf-8")
    return export_dir


@pytest.fixture
def test_settings(tmp_path: Path, meetily_export_dir: Path) -> Settings:
    return Settings(
        provider="anthropic",  # unused whenever provider= is injected directly into create_app
        anthropic_api_key=None,
        anthropic_model="claude-sonnet-5",
        scaleway_api_key=None,
        scaleway_model="glm-5.2",
        scaleway_base_url="https://api.scaleway.ai/v1",
        database_path=tmp_path / "app.db",
        download_dir=tmp_path / "downloads",
        meetily_source_mode="export_folder",
        meetily_source_path=meetily_export_dir,
        admin_username=None,
        admin_password=None,
        host="127.0.0.1",
        port=8000,
    )
