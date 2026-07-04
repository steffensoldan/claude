"""Scaleway-backed TranslationProvider (OpenAI-compatible Generative APIs).
Target for the later migration phase, model GLM 5.2 (model ID to be verified
at runtime via GET /v1/models against a real Scaleway key — not guessed)."""
from __future__ import annotations

import openai

from ._prompts import SUMMARIZE_SYSTEM_PROMPT, TRANSLATE_SYSTEM_PROMPT
from .base import ProviderError, TranslationProvider, TranslationResult


class ScalewayProvider(TranslationProvider):
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://api.scaleway.ai/v1",
        client: openai.OpenAI | None = None,
    ) -> None:
        self._model = model
        self._client = client or openai.OpenAI(api_key=api_key, base_url=base_url)

    def translate(self, transcript_text: str, *, target_language: str = "de") -> TranslationResult:
        system = TRANSLATE_SYSTEM_PROMPT.format(target_language=target_language)
        text = self._complete(system, transcript_text)
        return TranslationResult(translated_text=text, model_used=self._model)

    def summarize(self, transcript_text: str, *, language: str = "de") -> str:
        system = SUMMARIZE_SYSTEM_PROMPT.format(language=language)
        return self._complete(system, transcript_text)

    def _complete(self, system: str, user_text: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_text},
                ],
            )
        except openai.OpenAIError as exc:
            raise ProviderError(f"Scaleway request failed: {exc}") from exc

        choice = response.choices[0] if response.choices else None
        if choice is None or choice.message.content is None:
            raise ProviderError("Scaleway response contained no content")
        return choice.message.content
