from __future__ import annotations

from typing import Any, Dict, List

import openai

from beeflow_ai.openai_chat_completition_client import OpenAIChatCompletionClient


class _StubMessage:
    def __init__(self, content: str | None) -> None:
        self.content = content


class _StubChoice:
    def __init__(self, content: str | None) -> None:
        self.message = _StubMessage(content)


class _StubResponse:
    def __init__(self, content: str | None) -> None:
        self.choices = [_StubChoice(content)]


class StubCreate:
    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []

    def __call__(self, *, model, messages, top_p, **kwargs):  # type: ignore[no-redef]
        # Record exact args/kwargs to assert behavior (esp. max_tokens presence).
        self.calls.append(
            {
                "model": model,
                "messages": messages,
                "top_p": top_p,
                **kwargs,
            }
        )
        return _StubResponse("  hello  ")


def test_create_strips_content_and_passes_params(monkeypatch):
    stub = StubCreate()
    client = OpenAIChatCompletionClient(api_key="key", openai_create=stub)

    # Case A: max_tokens omitted when None
    out = client.create(
        model_name="m",
        messages=[{"role": "user", "content": "x"}],
        max_tokens=None,
        top_p=0.7,
    )
    assert out == "hello"
    assert stub.calls[-1]["model"] == "m"
    assert stub.calls[-1]["top_p"] == 0.7
    assert "max_tokens" not in stub.calls[-1]
    assert isinstance(stub.calls[-1]["messages"], list)
    assert stub.calls[-1]["messages"][0]["role"] == "user"

    # Case B: max_tokens included when provided
    out = client.create(
        model_name="m2",
        messages=[{"role": "user", "content": "y"}],
        max_tokens=42,
        top_p=1.0,
    )
    assert out == "hello"
    assert stub.calls[-1]["model"] == "m2"
    assert stub.calls[-1]["top_p"] == 1.0
    assert stub.calls[-1]["max_tokens"] == 42


def test_reads_api_key_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    _ = OpenAIChatCompletionClient()  # no explicit key
    assert openai.api_key == "env-key"
