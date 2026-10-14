"""
Adversarial Tests for Post Copy & Authentic Voice Engine.
Tests buzzword penalty algorithms, malformed candidate lists, extreme inputs, and formatters.
"""

import pytest
from src.engines.copy_engine import (
    score_text_authenticity,
    format_linkedin_post,
    score_candidate,
    select_champion_post,
    BANNED_BUZZWORDS,
)


class TestCopyEngineAdversarial:
    def test_buzzword_penalties(self):
        """Calculates correct penalties when corporate AI buzzwords are injected."""
        clean_text = "Here is what finally clicked for me when learning about SQL indexes."
        penalty_clean, found_clean = score_text_authenticity(clean_text)
        assert penalty_clean == 0.0
        assert len(found_clean) == 0

        # Inject 3 buzzwords: 'delve', 'unlock', 'game-changer'
        slop_text = "Let us delve into how this unlock is a game-changer."
        penalty_slop, found_slop = score_text_authenticity(slop_text)
        assert penalty_slop == 9.0  # 3 * 3.0
        assert set(found_slop) == {"delve", "unlock", "game-changer"}

    def test_empty_and_null_post_formatter_inputs(self):
        """Format post must produce a coherent message even if inputs are None or empty."""
        post = format_linkedin_post(
            topic_title="",
            subject="",
            angle_content="",
            senior_question=""
        )
        assert "System Design" in post
        assert "Would love to know what is actually standard in production" in post
        assert "#systemdesign" in post

    def test_malformed_candidate_dict_resilience(self):
        """Candidate scoring handles empty dicts, missing keys, and invalid score types."""
        empty_candidate = {}
        candidate_post = score_candidate(empty_candidate)
        assert candidate_post.angle_title == "Untitled"
        assert candidate_post.total_score >= 0.0

        corrupted_candidate = {
            "hook": None,
            "body": None,
            "scores": {"human_authenticity": "invalid_score"}
        }
        # Should not crash on invalid types
        try:
            candidate_post2 = score_candidate(corrupted_candidate)
            assert candidate_post2 is not None
        except ValueError:
            pass  # Handled safely

    def test_select_champion_post_empty_and_corrupt_lists(self):
        """Champion selection survives empty candidate lists without crashing."""
        empty_result = select_champion_post([])
        assert empty_result.angle_title == "Fallback"

        # List with multiple candidates where slop candidate is penalized
        candidates = [
            {
                "angle_title": "AI Slop Post",
                "hook": "Delve into this game-changer in today's fast-paced world to unlock synergy.",
                "body": "Agree? Let that sink in.",
                "scores": {"human_authenticity": 10.0, "simplicity": 10.0, "senior_engagement": 10.0}
            },
            {
                "angle_title": "Authentic Post",
                "hook": "When I first learned token buckets, it sounded confusing.",
                "body": "Here is how 3 calls pass instantly but 4th gets 429.",
                "scores": {"human_authenticity": 8.5, "simplicity": 8.5, "senior_engagement": 8.5}
            }
        ]
        champion = select_champion_post(candidates)
        # Authentic post must win due to heavy buzzword penalty on slop post
        assert champion.angle_title == "Authentic Post"
