"""Anthropic-backed TranslationProvider. Used for the initial test phase
(PROVIDER=anthropic), model claude-sonnet-5 per project decision."""
from __future__ import annotations

import anthropic

from ._prompts import SUMMARIZE_SYSTEM_PROMPT, TRANSLATE_SYSTEM_PROMPT
from .base import ProviderError, TranslationProvider, TranslationResult

_MAX_TOKENS = 8192


class AnthropicProvider(TranslationProvider):
    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-5",
        client: anthropic.Anthropic | None = None,
    ) -> None:
        self._model = model
        self._client = client or anthropic.Anthropic(api_key=api_key)

    def translate(self, transcript_text: str, *, target_language: str = "de") -> TranslationResult:
        system = TRANSLATE_SYSTEM_PROMPT.format(target_language=target_language)
        text = self._complete(system, transcript_text)
        return TranslationResult(translated_text=text, model_used=self._model)

    def summarize(self, transcript_text: str, *, language: str = "de") -> str:
        system = SUMMARIZE_SYSTEM_PROMPT.format(language=language)
        return self._complete(system, transcript_text)

    def _complete(self, system: str, user_text: str) -> str:
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=_MAX_TOKENS,
                system=system,
                messages=[{"role": "user", "content": user_text}],
            )
        except (anthropic.APIStatusError, anthropic.APIConnectionError) as exc:
            raise ProviderError(f"Anthropic request failed: {exc}") from exc

        text_blocks = [block.text for block in response.content if block.type == "text"]
        if not text_blocks:
            raise ProviderError("Anthropic response contained no text content")
        return "".join(text_blocks)
