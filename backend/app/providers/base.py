"""Provider-neutral interface for LLM-backed translation/summarization.

Two native SDK implementations exist (anthropic_provider.py, scaleway_provider.py)
rather than a meta-framework (e.g. LiteLLM) — keeps each provider's error
handling and request shape transparent, avoids an extra heavy dependency.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class ProviderError(Exception):
    """Raised when a translation provider fails; wraps SDK-specific errors
    so callers never need to catch anthropic.* / openai.* exceptions directly."""


@dataclass(frozen=True)
class TranslationResult:
    translated_text: str
    model_used: str


class TranslationProvider(ABC):
    @abstractmethod
    def translate(self, transcript_text: str, *, target_language: str = "de") -> TranslationResult:
        """Translate a transcript into target_language (ISO 639-1 code)."""

    @abstractmethod
    def summarize(self, transcript_text: str, *, language: str = "de") -> str:
        """Produce a bullet-point summary of a transcript in the given language."""
