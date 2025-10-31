"""Beeflow AI Toolkit: lekkie narzędzia do pracy z modelami AI.

Publiczne API dostarcza klienta Chat Completions, prosty rejestr generatorów
treści, walidator JSON Schema i budowniczych promptów (np. feedback pokerowy).
"""

from __future__ import annotations

from .generator.poker_feedback_generator import PokerFeedbackGenerator
from .json_schema_validator import JsonSchemaValidator, SchemaValidatorLoader
from .loader import load_schema
from .openai_chat_completition_client import (
    BaseContentGenerator,
    ChatCompletionClient,
    ContentGeneratorRegistry,
    OpenAIChatCompletionClient,
    PromptBuilder,
    register_content_generator,
)
from .prompt_builder import PokerFeedbackPromptBuilder, PokerStats

__all__ = [
    "JsonSchemaValidator",
    "SchemaValidatorLoader",
    "load_schema",
    "OpenAIChatCompletionClient",
    "BaseContentGenerator",
    "PromptBuilder",
    "ChatCompletionClient",
    "ContentGeneratorRegistry",
    "register_content_generator",
    "PokerFeedbackPromptBuilder",
    "PokerFeedbackGenerator",
    "PokerStats",
]
