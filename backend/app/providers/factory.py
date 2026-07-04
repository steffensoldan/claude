"""Fail-closed provider selection: unknown/missing PROVIDER setting is an
error, never a silent fallback."""
from __future__ import annotations

from ..config import Settings
from .anthropic_provider import AnthropicProvider
from .base import TranslationProvider
from .scaleway_provider import ScalewayProvider


class ProviderConfigurationError(Exception):
    """Raised when PROVIDER is missing/unknown or a required setting is absent."""


def get_provider(settings: Settings) -> TranslationProvider:
    provider_name = (settings.provider or "").strip().lower()

    if provider_name == "anthropic":
        if not settings.anthropic_api_key:
            raise ProviderConfigurationError(
                "ANTHROPIC_API_KEY is required when PROVIDER=anthropic"
            )
        return AnthropicProvider(api_key=settings.anthropic_api_key, model=settings.anthropic_model)

    if provider_name == "scaleway":
        if not settings.scaleway_api_key:
            raise ProviderConfigurationError(
                "SCALEWAY_API_KEY is required when PROVIDER=scaleway"
            )
        return ScalewayProvider(
            api_key=settings.scaleway_api_key,
            model=settings.scaleway_model,
            base_url=settings.scaleway_base_url,
        )

    raise ProviderConfigurationError(
        f"Unknown or missing PROVIDER setting: {settings.provider!r}. "
        "Expected 'anthropic' or 'scaleway'."
    )
