from __future__ import annotations

from typing import Any, Dict, List, Optional

from beeflow_ai.generator.poker_feedback_generator import PokerFeedbackGenerator
from beeflow_ai.openai_chat_completition_client import ChatCompletionClient
from beeflow_ai.prompt_builder import PokerFeedbackPromptBuilder, PokerStats


class StubClient(ChatCompletionClient):
    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []

    def create(
        self,
        *,
        model_name: str,
        messages: list,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
    ) -> str:
        self.calls.append(
            {
                "model_name": model_name,
                "messages": messages,
                "max_tokens": max_tokens,
                "top_p": top_p,
            }
        )
        return "x" * 100  # long content to test trimming


def test_generate_builds_messages_passes_params_and_trims_output():
    stats: PokerStats = {"hands_played": 123}
    client = StubClient()
    gen = PokerFeedbackGenerator(
        chat_completion_client=client,
        model_name="gpt-X",
        builder_factory=lambda s: PokerFeedbackPromptBuilder(s, max_chars=12),
    )

    out = gen.generate(stats, top_p=0.8, max_tokens=64)
    assert len(out) <= 12
    assert out == "x" * 12

    call = client.calls[-1]
    assert call["model_name"] == "gpt-X"
    assert call["top_p"] == 0.8
    assert call["max_tokens"] == 64
    assert isinstance(call["messages"], list)
    assert call["messages"][0]["role"] == "system"
    assert "plain text only" in call["messages"][0]["content"]
    assert call["messages"][1]["role"] == "user"
    assert call["messages"][1]["content"].startswith("Provide concise poker coaching feedback")
