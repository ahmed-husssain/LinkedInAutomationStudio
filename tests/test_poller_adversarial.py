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

    def test_intent_matching_direct_format_requests(self):
        """Conversational format requests for active topic route to GENERATE_ACTIVE_FORMAT."""
        res_vid = match_user_intent("I want to make a video animation of that", TOPIC_POOL[0])
        assert res_vid["intent"] == "GENERATE_ACTIVE_FORMAT"
        assert res_vid["format"] == "video"

        res_car = match_user_intent("can you make a carousel for this?", TOPIC_POOL[0])
        assert res_car["intent"] == "GENERATE_ACTIVE_FORMAT"
        assert res_car["format"] == "carousel"

        res_diag = match_user_intent("show me the architecture diagram", TOPIC_POOL[0])
        assert res_diag["intent"] == "GENERATE_ACTIVE_FORMAT"
        assert res_diag["format"] == "diagram"

    def test_animation_consultation_dispatch_and_chat_followup(self):
        """Video requests launch consultation view; subsequent chat reply captures custom issue."""
        from src.bot.poller import dispatch_user_message
        from src.bot.views import CHANNEL_ACTIVE_TOPIC, CHANNEL_CONSULTATION_STATE, AnimationConsultationView
        from unittest.mock import AsyncMock, MagicMock, patch

        async def _run():
            mock_channel = AsyncMock()
            mock_channel.id = 888123
            mock_author = MagicMock()
            mock_author.mention = "@testuser"

            rate_topic = next(t for t in TOPIC_POOL if t.id == "rate_limiter")
            CHANNEL_ACTIVE_TOPIC[mock_channel.id] = rate_topic
            CHANNEL_CONSULTATION_STATE.pop(mock_channel.id, None)

            # Step 1: User says "I want to make a video animation of that"
            await dispatch_user_message(
                channel=mock_channel,
                author=mock_author,
                raw_text="I want to make a video animation of that"
            )

            # Must have sent AnimationConsultationView and set consultation state
            mock_channel.send.assert_called_once()
            send_args = mock_channel.send.call_args[1]
            assert isinstance(send_args["view"], AnimationConsultationView)
            assert "Animation Studio Consultation" in send_args["content"]
            assert mock_channel.id in CHANNEL_CONSULTATION_STATE

            # Step 2: User replies with custom issue in chat
            mock_channel.reset_mock()
            with patch("src.bot.views.deliver_post_package", new_callable=AsyncMock) as mock_deliver:
                await dispatch_user_message(
                    channel=mock_channel,
                    author=mock_author,
                    raw_text="Our payment gateway locks up when 5,000 users checkout during flash sales"
                )
                # Consultation state must be cleared
                assert mock_channel.id not in CHANNEL_CONSULTATION_STATE
                # Acknowledgment message must be sent
                mock_channel.send.assert_called_once()
                ack_text = mock_channel.send.call_args[1]["content"]
                assert "Custom Setup Captured" in ack_text
                # deliver_post_package must be triggered with custom hook
                mock_deliver.assert_called_once()
                deliver_kwargs = mock_deliver.call_args[1]
                assert "payment gateway locks up" in deliver_kwargs["custom_hook"]
                assert deliver_kwargs["format_type"] == "video"

        import asyncio
        asyncio.run(_run())


