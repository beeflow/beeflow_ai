from __future__ import annotations

"""Prompt builder for concise poker session feedback.

This module defines `PokerFeedbackPromptBuilder`, which builds a compact, deterministic
prompt instructing a chat model to produce short coach-style feedback based on user poker
statistics. The output must be plain text suitable for mobile and web, avoiding emojis
and formatting.

All comments and docstrings use British English spelling. Lines are kept under 100 chars.
"""

from dataclasses import dataclass
from typing import Iterable, Mapping, TypedDict


class PokerStats(TypedDict, total=False):
    """Minimal set of poker session statistics expected by the builder.

    Values should be pre-aggregated for a single session. Rates are percentages in [0, 100].
    All numeric values are expected to be non-negative.
    """

    hands_played: int
    vpip: float  # Voluntarily Put Money In Pot %
    pfr: float  # Pre-Flop Raise %
    three_bet: float  # 3-bet %
    aggression_factor: float
    showdown_win_rate: float  # % of showdowns won
    net_profit_bb: int  # Net profit in big blinds
    session_minutes: int
    strengths: list[str]
    leaks: list[str]


@dataclass(slots=True)
class PokerFeedbackPromptBuilder:
    """Build a concise instruction prompt for poker feedback generation.

    The builder produces a stable prompt embedding the provided stats as compact key:value
    pairs, along with strict constraints for output style and length. The model must reply
    with 2-3 sentences of plain text in the selected language.
    """

    stats: PokerStats
    language_code: str = "pl"
    max_chars: int = 280
    tone: str = "neutral"

    def build(self) -> str:
        """Return a complete user prompt for the LLM.

        The prompt contains:
        - Audience and constraints (language, length, no formatting, 2-3 sentences).
        - Compact, rounded statistics to ground the response.
        - Focus guidance: highlight 1–2 strengths and 1–2 improvements.
        """
        header = (
            "Provide concise poker coaching feedback based on the session stats below. "
            f"Respond in {self.language_code}. Use 2-3 sentences, max {self.max_chars} "
            "characters, plain text only (no emojis, no markdown, no lists). Focus on "
            "1-2 strengths and 1-2 clear improvements."
        )

        stats_line = self._format_stats(self.stats)
        tone_line = self._tone_hint(self.tone)
        return f"{header}\nTone:{tone_line}\nStats:{stats_line}"

    @staticmethod
    def _tone_hint(tone: str) -> str:
        """Return a short tone hint; defaults to neutral if empty.

        We avoid branches by mapping known tones; unknown values fall back to neutral.
        """
        tone_map: Mapping[str, str] = {
            "neutral": "balanced, constructive",
            "friendly": "friendly, encouraging",
            "direct": "direct, actionable",
        }
        key = (tone or "").strip().lower()
        return tone_map.get(key, tone_map["neutral"])

    @staticmethod
    def _fmt_val(value: object) -> str:
        """Format a scalar value compactly with limited precision.

        - Integers rendered as is
        - Floats rounded to 1 decimal
        - Other objects stringified safely
        """
        if isinstance(value, int):
            return str(value)
        if isinstance(value, float):
            return f"{value:.1f}"
        return str(value)

    @classmethod
    def _format_stats(cls, stats: PokerStats) -> str:
        """Return a single-line compact representation of key stats.

        Only includes known, non-missing keys in a fixed order to keep prompts stable.
        Lists are joined with '; ' when present.
        """
        order: list[tuple[str, str]] = [
            ("hands_played", "hands"),
            ("vpip", "vpip%"),
            ("pfr", "pfr%"),
            ("three_bet", "3bet%"),
            ("aggression_factor", "AF"),
            ("showdown_win_rate", "sd_win%"),
            ("net_profit_bb", "profit_bb"),
            ("session_minutes", "mins"),
        ]
        parts: list[str] = []
        for key, label in order:
            if key in stats:
                parts.append(f"{label}:{cls._fmt_val(stats[key])}")
        strengths = stats.get("strengths")
        leaks = stats.get("leaks")
        if strengths:
            parts.append(f"strengths:{cls._join(strengths)}")
        if leaks:
            parts.append(f"leaks:{cls._join(leaks)}")
        return " ".join(parts)

    @staticmethod
    def _join(items: Iterable[str]) -> str:
        """Join short strings with '; ' safely, trimming whitespace."""
        cleaned = [s.strip() for s in items if s and s.strip()]
        return "; ".join(cleaned) if cleaned else ""
