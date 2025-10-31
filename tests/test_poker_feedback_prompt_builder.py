from __future__ import annotations

from beeflow_ai.prompt_builder import PokerFeedbackPromptBuilder, PokerStats


def test_build_includes_header_tone_and_stats_in_expected_format():
    stats: PokerStats = {
        "hands_played": 120,
        "vpip": 28.3,
        "pfr": 22.1,
        "three_bet": 9.6,
        "aggression_factor": 2.7,
        "showdown_win_rate": 55.0,
        "net_profit_bb": 35,
        "session_minutes": 75,
        "strengths": ["Value-betting", "Discipline"],
        "leaks": [" Calling 3-bets too wide ", " "],
    }

    builder = PokerFeedbackPromptBuilder(
        stats=stats,
        language_code="en",
        max_chars=160,
        tone="friendly",
    )
    prompt = builder.build()

    assert "Respond in en" in prompt
    assert "max 160" in prompt
    assert "Tone:friendly, encouraging" in prompt

    # Stats line should contain compact keys and joined lists
    assert "hands:120" in prompt
    assert "vpip%:28.3" in prompt
    assert "pfr%:22.1" in prompt
    assert "3bet%:9.6" in prompt
    assert "AF:2.7" in prompt
    assert "sd_win%:55.0" in prompt
    assert "profit_bb:35" in prompt
    assert "mins:75" in prompt
    assert "strengths:Value-betting; Discipline" in prompt
    assert "leaks:Calling 3-bets too wide" in prompt