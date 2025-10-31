"""Prompt builder package for AI content generation.

This package hosts builder classes responsible for composing deterministic prompts
for different AI tasks. Keeping builders here separates prompt composition from content
generation logic and improves reuse and testability.

All comments and docstrings use British English spelling.
"""
from __future__ import annotations

from .poker_feedback_prompt_builder import PokerFeedbackPromptBuilder, PokerStats

__all__ = [
    "PokerFeedbackPromptBuilder",
    "PokerStats",
]
