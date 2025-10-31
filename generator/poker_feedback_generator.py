from __future__ import annotations

"""Content generator for concise poker session feedback.

This module defines `PokerFeedbackGenerator`, which composes a deterministic prompt using
`PokerFeedbackPromptBuilder` and generates short, plain-text feedback using a chat-based model.
The generator is decoupled from the OpenAI SDK via the `ChatCompletionClient` protocol.

All comments and docstrings use British English spelling.
"""

import os
from typing import Callable, Optional

from openai.types.chat import ChatCompletionMessageParam

from ..openai_chat_completition_client import (
    BaseContentGenerator,
    ChatCompletionClient,
    PromptBuilder,
)
from ..prompt_builder import PokerFeedbackPromptBuilder, PokerStats


class PokerFeedbackGenerator(BaseContentGenerator):
    """Generate concise poker feedback grounded in user session statistics.

    The generator uses dependency injection for the chat completion client and a builder
    factory to prepare per-request prompts. The output is trimmed to the maximum number of
    characters requested by the builder to ensure suitability for mobile and web UIs.
    """

    builder_factory: Callable[[PokerStats], PromptBuilder]

    def __init__(
        self,
        *,
        chat_completion_client: ChatCompletionClient,
        model_name: str | None = None,
        builder_factory: Callable[[PokerStats], PromptBuilder] | None = None,
    ) -> None:
        # Fallbacks are environmental to keep configuration outside code.
        resolved_model = model_name or os.environ.get("POKER_FEEDBACK_MODEL", "gpt-5")
        # Provide a harmless default builder instance for the base class; real builders are
        # produced per-call by `builder_factory`.
        default_stats: PokerStats = {}
        default_builder = (builder_factory or (lambda s: PokerFeedbackPromptBuilder(s)))(default_stats)
        super().__init__(
            prompt_builder=default_builder,
            chat_completion_client=chat_completion_client,
            schema_validator=None,
            model_name=resolved_model,
        )
        self.builder_factory = builder_factory or (lambda s: PokerFeedbackPromptBuilder(s))

    def generate(
        self,
        stats: PokerStats,
        *,
        top_p: float = 0.9,
        max_tokens: Optional[int] = 120,
    ) -> str:
        """Return concise feedback for the given poker session statistics.

        The function builds a pair of chat messages (system + user) and delegates to the
        injected chat client. The returned text is trimmed to the max character limit
        requested by the builder to guarantee UI constraints.
        """
        builder = self.builder_factory(stats)
        prompt = builder.build()

        system_msg: ChatCompletionMessageParam = {
            "role": "system",
            "content": (
                "You are an expert poker coach. Follow the instructions strictly. "
                "Answer with plain text only (no emojis, no markdown)."
            ),
        }
        user_msg: ChatCompletionMessageParam = {"role": "user", "content": prompt}
        messages: list[ChatCompletionMessageParam] = [system_msg, user_msg]

        content = self.chat_completion_client.create(
            model_name=self.model_name,
            messages=messages,
            max_tokens=max_tokens,
            top_p=top_p,
        )

        text = (content or "").strip()
        # Enforce the max character length contract to protect downstream UIs.
        max_chars = getattr(builder, "max_chars", 280)
        if len(text) <= max_chars:
            return text
        return text[:max_chars].rstrip()
