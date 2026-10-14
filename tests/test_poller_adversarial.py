"""
Adversarial Tests for Message Poller & Deduplication Tracker.
Tests bounded memory constraints, injection strings, zero-width characters, and intent matching.
"""

import pytest
from src.bot.poller import (
    BoundedMessageTracker,
    clean_discord_mentions,
    match_user_intent,
)
from src.config.topics import TOPIC_POOL


class TestPollerAdversarial:
    def test_bounded_memory_under_extreme_volume(self):
        """Feeding 10,000 unique message IDs must strictly cap memory at max_size (no leak)."""
        max_size = 50
        tracker = BoundedMessageTracker(max_size=max_size)

        for i in range(10000):
            tracker.add(i)

        assert len(tracker) == max_size
        # The oldest items (0..9949) should have been evicted
        assert 0 not in tracker
        assert 5000 not in tracker
        # The latest items should be present
        assert 9999 in tracker
        assert 9998 in tracker

    def test_duplicate_rejection(self):
        """Duplicate message IDs must be identified instantly (O(1))."""
        tracker = BoundedMessageTracker(max_size=100)
        assert tracker.add(123456789) is False  # First seen: not duplicate
        assert tracker.add(123456789) is True   # Second seen: duplicate rejected
        assert 123456789 in tracker

    def test_mention_cleaning_adversarial_inputs(self):
        """Strips nested tags, invisible unicode, null bytes, and malicious control chars."""
        # 1. Null bytes and control codes
        dirty1 = "Hello \x00\x01\x1f World!"
        assert clean_discord_mentions(dirty1) == "Hello World!"

        # 2. Zero-width spaces used to evade filters
        dirty2 = "o\u200ba\u200bu\u200bt\u200bh"
        assert clean_discord_mentions(dirty2) == "oauth"

        # 3. Discord mention patterns
        dirty3 = "<@!123456789> @LinkedIn Studio <#987654321> <@&55555> check oauth please"
        assert clean_discord_mentions(dirty3, bot_name="LinkedIn Studio") == "check oauth please"

        # 4. Empty or None input
        assert clean_discord_mentions(None) == ""
        assert clean_discord_mentions("") == ""

    def test_intent_matching_sql_and_script_injection(self):
        """SQL injection or shell strings should not throw exceptions or crash intent engine."""
        sql_string = "' OR '1'='1; DROP TABLE users; --"
        res_sql = match_user_intent(sql_string, TOPIC_POOL[0])
        assert res_sql["intent"] in ["FALLBACK", "BROWSE_TOPICS", "TOPIC_MATCH"]

        shell_string = "$(rm -rf /) ; touch test.txt"
        res_shell = match_user_intent(shell_string, TOPIC_POOL[0])
        assert res_shell["intent"] in ["FALLBACK", "BROWSE_TOPICS", "TOPIC_MATCH"]

    def test_intent_matching_keyword_priority(self):
        """Keywords like 'queue' must route to message_queues regardless of word order."""
        res_q = match_user_intent("can you explain rabbitmq and buffer queue?", TOPIC_POOL[0])
        assert res_q["intent"] == "TOPIC_MATCH"
        assert res_q["topic"].id == "message_queues"

        res_thumb = match_user_intent("change thumbnail color", TOPIC_POOL[0])
        assert res_thumb["intent"] == "THUMBNAIL_OPTIONS"

        res_simple = match_user_intent("this is confusing, give me a simpler explanation", TOPIC_POOL[0])
        assert res_simple["intent"] == "SIMPLIFY"
