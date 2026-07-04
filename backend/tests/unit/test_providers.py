from __future__ import annotations

from pathlib import Path

import pytest

from app.config import Settings
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.base import ProviderError
from app.providers.factory import ProviderConfigurationError, get_provider
from app.providers.scaleway_provider import ScalewayProvider


# --- Anthropic provider, against a fake SDK client (no network) ---


class _FakeAnthropicTextBlock:
    def __init__(self, text: str) -> None:
        self.type = "text"
        self.text = text


class _FakeAnthropicMessage:
    def __init__(self, text: str) -> None:
        self.content = [_FakeAnthropicTextBlock(text)]


class _FakeAnthropicMessages:
    def __init__(self, response_text: str) -> None:
        self._response_text = response_text
        self.last_kwargs: dict | None = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return _FakeAnthropicMessage(self._response_text)


class _FakeAnthropicClient:
    def __init__(self, response_text: str = "Hallo Welt") -> None:
        self.messages = _FakeAnthropicMessages(response_text)


def test_anthropic_provider_translate_returns_text():
    client = _FakeAnthropicClient(response_text="Hallo Welt")
    provider = AnthropicProvider(api_key="unused", model="claude-sonnet-5", client=client)

    result = provider.translate("Hello world", target_language="de")

    assert result.translated_text == "Hallo Welt"
    assert result.model_used == "claude-sonnet-5"
    assert "de" in client.messages.last_kwargs["system"]


def test_anthropic_provider_summarize_returns_text():
    client = _FakeAnthropicClient(response_text="- Punkt 1")
    provider = AnthropicProvider(api_key="unused", client=client)

    summary = provider.summarize("Some transcript")

    assert summary == "- Punkt 1"


def test_anthropic_provider_wraps_empty_content_as_provider_error():
    class _EmptyMessages:
        def create(self, **kwargs):
            class _Msg:
                content: list = []

            return _Msg()

    class _EmptyClient:
        messages = _EmptyMessages()

    provider = AnthropicProvider(api_key="unused", client=_EmptyClient())

    with pytest.raises(ProviderError):
        provider.translate("text")


# --- Scaleway provider, against a fake OpenAI-compatible SDK client ---


class _FakeOpenAIChoiceMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class _FakeOpenAIChoice:
    def __init__(self, content: str) -> None:
        self.message = _FakeOpenAIChoiceMessage(content)


class _FakeOpenAIResponse:
    def __init__(self, content: str) -> None:
        self.choices = [_FakeOpenAIChoice(content)]


class _FakeOpenAICompletions:
    def __init__(self, response_text: str) -> None:
        self._response_text = response_text

    def create(self, **kwargs):
        return _FakeOpenAIResponse(self._response_text)


class _FakeOpenAIChat:
    def __init__(self, response_text: str) -> None:
        self.completions = _FakeOpenAICompletions(response_text)


class _FakeOpenAIClient:
    def __init__(self, response_text: str = "Hallo Welt") -> None:
        self.chat = _FakeOpenAIChat(response_text)


def test_scaleway_provider_translate_returns_text():
    client = _FakeOpenAIClient(response_text="Hallo Welt")
    provider = ScalewayProvider(api_key="unused", model="glm-5.2", client=client)

    result = provider.translate("Hello world", target_language="de")

    assert result.translated_text == "Hallo Welt"
    assert result.model_used == "glm-5.2"


def test_scaleway_provider_wraps_missing_choice_as_provider_error():
    class _EmptyCompletions:
        def create(self, **kwargs):
            class _Resp:
                choices: list = []

            return _Resp()

    class _EmptyChat:
        completions = _EmptyCompletions()

    class _EmptyClient:
        chat = _EmptyChat()

    provider = ScalewayProvider(api_key="unused", model="glm-5.2", client=_EmptyClient())

    with pytest.raises(ProviderError):
        provider.translate("text")


# --- Factory: fail-closed behavior ---


def _base_settings(**overrides) -> Settings:
    defaults = dict(
        provider="anthropic",
        anthropic_api_key=None,
        anthropic_model="claude-sonnet-5",
        scaleway_api_key=None,
        scaleway_model="glm-5.2",
        scaleway_base_url="https://api.scaleway.ai/v1",
        database_path=Path("unused.db"),
        download_dir=Path("unused_downloads"),
        meetily_source_mode="export_folder",
        meetily_source_path=Path("unused_exports"),
        admin_username=None,
        admin_password=None,
        host="127.0.0.1",
        port=8000,
    )
    defaults.update(overrides)
    return Settings(**defaults)


def test_factory_fails_closed_on_unknown_provider():
    with pytest.raises(ProviderConfigurationError):
        get_provider(_base_settings(provider="bogus"))


def test_factory_requires_anthropic_key():
    with pytest.raises(ProviderConfigurationError):
        get_provider(_base_settings(provider="anthropic", anthropic_api_key=None))


def test_factory_requires_scaleway_key():
    with pytest.raises(ProviderConfigurationError):
        get_provider(_base_settings(provider="scaleway", scaleway_api_key=None))


def test_factory_builds_anthropic_provider_when_key_present():
    provider = get_provider(_base_settings(provider="anthropic", anthropic_api_key="sk-ant-test"))
    assert isinstance(provider, AnthropicProvider)


def test_factory_builds_scaleway_provider_when_key_present():
    provider = get_provider(_base_settings(provider="scaleway", scaleway_api_key="scw-test"))
    assert isinstance(provider, ScalewayProvider)
