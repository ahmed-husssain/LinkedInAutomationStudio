"""
Adversarial & Unit Tests for Multi-Agent Studio Orchestrator and Dispatcher.
Verifies:
1. Absence of NameError / missing import crashes.
2. Direct in-line reply routing for layout/video feedback.
3. Intent routing for status/greeting and generation requests.
4. Robust error boundaries when Discord API fails.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from src.agents.orchestrator import AgentStudioOrchestrator
from src.bot.poller import dispatch_user_message
from src.config.topics import TOPIC_POOL


class DummyMessage:
    def __init__(self, content: str, author_name: str = "ahmedd_dev321_86764"):
        self.content = content
        self.clean_content = content
        self.id = 123456789
        self.channel = AsyncMock()
        self.channel.id = 987654321
        self.channel.send = AsyncMock()
        self.author = MagicMock()
        self.author.mention = f"@{author_name}"
        self.author.name = author_name
        self.author.bot = False
        self.reply = AsyncMock()


def test_video_overlap_feedback_routing():
    """Verifies that feedback on video/layout triggers the layout overhaul reply with assets."""
    async def _test():
        orchestrator = AgentStudioOrchestrator()
        msg = DummyMessage("this video is overlapping the text div's on each other")

        await orchestrator.handle_conversational_request(msg, msg.content)

        msg.reply.assert_called_once()
        call_kwargs = msg.reply.call_args.kwargs
        assert "Video Layout Overhaul Complete" in call_kwargs["content"]
        assert "Bottom HUD Safe Zone" in call_kwargs["content"]
        assert call_kwargs.get("mention_author") is True

    asyncio.run(_test())


def test_status_and_greeting_routing():
    """Verifies that queries asking why no reply or greetings receive an active status reply."""
    async def _test():
        orchestrator = AgentStudioOrchestrator()
        msg = DummyMessage("response me i message a while ago still no respnse from other side")

        await orchestrator.handle_conversational_request(msg, msg.content)

        msg.reply.assert_called_once()
        call_kwargs = msg.reply.call_args.kwargs
        assert "online, active, and listening" in call_kwargs["content"]

    asyncio.run(_test())


def test_dispatch_user_message_does_not_crash_on_conversational_input():
    """Verifies dispatch_user_message handles freeform conversation without NameError."""
    async def _test():
        channel = AsyncMock()
        channel.id = 987654321
        channel.send = AsyncMock()
        author = MagicMock()
        author.mention = "@user"
        author.name = "user"
        author.bot = False
        msg = DummyMessage("what is the best way to handle kafka lag?")

        # Should dispatch cleanly without NameError: name 'asyncio' is not defined
        await dispatch_user_message(channel, author, msg.content, "LinkedIn Studio", message=msg)
        await asyncio.sleep(0.05)

    asyncio.run(_test())


def test_error_boundary_graceful_recovery():
    """Verifies that even if orchestrator throws an exception, it does not bubble up unhandled."""
    async def _test():
        orchestrator = AgentStudioOrchestrator()
        msg = DummyMessage("some unusual error trigger")

        with patch.object(orchestrator.gemini, "generate", side_effect=RuntimeError("Simulated API failure")):
            # Should catch gracefully and send error note without raising
            await orchestrator.handle_conversational_request(msg, msg.content)
            msg.reply.assert_called_once()
            assert "minor hiccup" in msg.reply.call_args.kwargs["content"]

    asyncio.run(_test())


def test_pleasantries_routing_does_not_lecture_architecture():
    """Verifies that saying 'good', 'thanks', etc. receives a warm acknowledgment, not architecture lecture."""
    async def _test():
        orchestrator = AgentStudioOrchestrator()
        msg = DummyMessage("good")

        await orchestrator.handle_conversational_request(msg, msg.content)

        msg.reply.assert_called_once()
        call_kwargs = msg.reply.call_args.kwargs
        assert "Glad to hear that" in call_kwargs["content"]
        assert "senior engineering perspective on good" not in call_kwargs["content"]

    asyncio.run(_test())


def test_trending_topics_discovery_routing():
    """Verifies that asking for better/interesting topics returns trending production topics."""
    async def _test():
        orchestrator = AgentStudioOrchestrator()
        msg = DummyMessage("suggest some more interesting topics instead of old built-in ones")

        await orchestrator.handle_conversational_request(msg, msg.content)

        msg.reply.assert_called_once()
        call_kwargs = msg.reply.call_args.kwargs
        assert "Viral Production Architecture Topics" in call_kwargs["content"]
        assert "Incident Hook" in call_kwargs["content"]
        assert "view" in call_kwargs

    asyncio.run(_test())


def test_user_complaint_about_old_topics_routes_to_ai_discovery():
    """Verifies user's exact phrasing triggers AI discovery rather than static BROWSE_TOPICS menu."""
    from src.bot.poller import match_user_intent
    user_phrase = "it still suggesting that old built-in topics instead of giving more interesting topics that can be explained in a video or pdf carousel"
    parsed = match_user_intent(user_phrase, TOPIC_POOL[0])
    # Must NOT be intercepted by BROWSE_TOPICS
    assert parsed["intent"] == "FALLBACK"


def test_carousel_delivery_pipeline():
    """Verifies delivering a carousel format compiles a valid PDF without exceptions."""
    from src.bot.views import deliver_post_package
    async def _test():
        channel = AsyncMock()
        channel.send = AsyncMock()
        topic = TOPIC_POOL[0]

        await deliver_post_package(
            channel=channel,
            topic=topic,
            angle_content=topic.angles[0].text,
            senior_question=topic.questions[0],
            format_type="carousel"
        )

        channel.send.assert_called_once()
        call_kwargs = channel.send.call_args.kwargs
        assert "YOUR READY-TO-POST LINKEDIN PACKAGE" in call_kwargs["content"]
        assert "PDF Carousel attached below" in call_kwargs["content"]
        assert "file" in call_kwargs
        assert call_kwargs["file"].filename.endswith("_Carousel.pdf")

    asyncio.run(_test())


def test_topic_selection_view_features():
    """Verifies TopicSelectionView has Carousel support and AI Viral Topics button."""
    from src.bot.views import TopicSelectionView, TopicConfiguratorView
    view = TopicSelectionView()
    assert len(view.current_topics) == 3
    # Check that AI Viral Topics button exists
    ai_btn = next((item for item in view.children if getattr(item, "label", "") == "🔥 AI Viral Topics"), None)
    assert ai_btn is not None

    cfg = TopicConfiguratorView(TOPIC_POOL[0])
    carousel_btn = next((item for item in cfg.children if "Carousel" in getattr(item, "label", "")), None)
    assert carousel_btn is not None



