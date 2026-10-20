"""
Unit and Adversarial Tests for Approval Gate Lock & Lifecycle State Machine.
Verifies channel locking, double-click rejection, approval vault promotion,
rejection instant purge, timeout auto-eviction, and emergency unlock.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from src.bot.views import (
    PostApprovalView,
    CHANNEL_PENDING_APPROVAL,
    TopicConfiguratorView,
)
from src.config.topics import TOPIC_POOL
from src.bot.poller import match_user_intent


def test_post_approval_view_approve(tmp_path: Path, monkeypatch):
    async def _run():
        channel_id = 999001
        draft_file = tmp_path / "test_deck.pdf"
        draft_file.write_text("dummy draft")

        # Mock published directory
        pub_dir = tmp_path / "published"
        pub_dir.mkdir()
        monkeypatch.setattr("src.engines.storage_manager.PUBLISHED_DIR", pub_dir)

        # Set channel lock
        CHANNEL_PENDING_APPROVAL[channel_id] = {"path": draft_file, "type": "carousel"}

        view = PostApprovalView(channel_id=channel_id, file_path=draft_file, post_text="sample post")

        # Mock Discord Interaction
        mock_interaction = MagicMock()
        mock_interaction.response.edit_message = AsyncMock()
        mock_interaction.message.content = "Initial post message"

        # Tap Approve
        await view.approve_button.callback(mock_interaction)

        # Lock must be released
        assert channel_id not in CHANNEL_PENDING_APPROVAL

        # File must be moved to published
        assert not draft_file.exists()
        assert (pub_dir / "test_deck.pdf").exists()

        # Buttons must be disabled
        for btn in view.children:
            assert btn.disabled is True

    asyncio.run(_run())


def test_post_approval_view_reject(tmp_path: Path):
    async def _run():
        channel_id = 999002
        draft_file = tmp_path / "rejected_draft.pdf"
        draft_file.write_text("bad draft")

        # Set channel lock
        CHANNEL_PENDING_APPROVAL[channel_id] = {"path": draft_file, "type": "carousel"}

        view = PostApprovalView(channel_id=channel_id, file_path=draft_file, post_text="sample post")

        mock_interaction = MagicMock()
        mock_interaction.response.edit_message = AsyncMock()
        mock_interaction.message.content = "Initial post message"

        # Tap Reject
        await view.reject_button.callback(mock_interaction)

        # Lock must be released
        assert channel_id not in CHANNEL_PENDING_APPROVAL

        # File must be wiped from disk
        assert not draft_file.exists()

        # Buttons must be disabled
        for btn in view.children:
            assert btn.disabled is True

    asyncio.run(_run())


def test_post_approval_view_timeout(tmp_path: Path):
    async def _run():
        channel_id = 999003
        draft_file = tmp_path / "abandoned_draft.pdf"
        draft_file.write_text("abandoned")

        CHANNEL_PENDING_APPROVAL[channel_id] = {"path": draft_file, "type": "carousel"}
        view = PostApprovalView(channel_id=channel_id, file_path=draft_file)

        # Trigger timeout
        await view.on_timeout()

        # Lock released & draft purged
        assert channel_id not in CHANNEL_PENDING_APPROVAL
        assert not draft_file.exists()

    asyncio.run(_run())


def test_topic_configurator_blocks_when_channel_locked():
    async def _run():
        channel_id = 999004
        CHANNEL_PENDING_APPROVAL[channel_id] = {"path": None, "type": "video"}

        topic = TOPIC_POOL[0]
        config_view = TopicConfiguratorView(topic=topic, selected_q="How does this scale?")

        mock_interaction = MagicMock()
        mock_interaction.channel_id = channel_id
        mock_interaction.response.send_message = AsyncMock()

        callback = config_view.make_format_callback("carousel")
        await callback(mock_interaction)

        # Block message sent ephemerally
        mock_interaction.response.send_message.assert_called_once()
        args, kwargs = mock_interaction.response.send_message.call_args
        assert "Action Blocked" in args[0]
        assert kwargs.get("ephemeral") is True

        # Cleanup
        CHANNEL_PENDING_APPROVAL.pop(channel_id, None)

    asyncio.run(_run())


def test_unlock_intent_regex():
    assert match_user_intent("unlock", TOPIC_POOL[0])["intent"] == "UNLOCK"
    assert match_user_intent("!unlock", TOPIC_POOL[0])["intent"] == "UNLOCK"
    assert match_user_intent("reset", TOPIC_POOL[0])["intent"] == "UNLOCK"
    assert match_user_intent("!clear_lock", TOPIC_POOL[0])["intent"] == "UNLOCK"


def test_post_rejection_recovery_view_actions():
    """Verifies that rejection recovery offers feedback and 1-tap rerouting."""
    from src.bot.views import PostRejectionRecoveryView

    async def _run():
        topic = TOPIC_POOL[0]
        recovery = PostRejectionRecoveryView(topic=topic, prev_format="diagram")

        content = recovery.get_message_content()
        assert "Draft Rejected & Purged" in content
        assert topic.title in content

        # Test feedback callback
        mock_interaction = MagicMock()
        mock_interaction.data = {"values": ["generic_hook"]}
        mock_interaction.response.send_message = AsyncMock()

        await recovery.feedback_callback(mock_interaction)
        mock_interaction.response.send_message.assert_called_once()
        args = mock_interaction.response.send_message.call_args[0][0]
        assert "Hook wasn't punchy" in args

        # Test switch format callback
        mock_interaction_format = MagicMock()
        mock_interaction_format.response.send_message = AsyncMock()
        await recovery.switch_format_callback(mock_interaction_format)
        mock_interaction_format.response.send_message.assert_called_once()

        # Test pick another topic callback
        mock_interaction_pick = MagicMock()
        mock_interaction_pick.response.send_message = AsyncMock()
        await recovery.pick_topic_callback(mock_interaction_pick)
        mock_interaction_pick.response.send_message.assert_called_once()

    asyncio.run(_run())


def test_animation_consultation_view_interactions():
    """Verifies that AnimationConsultationView asks what animation type and production issue, and renders tailored content."""
    from src.bot.views import AnimationConsultationView

    async def _run():
        rate_topic = next(t for t in TOPIC_POOL if t.id == "rate_limiter")
        consult = AnimationConsultationView(topic=rate_topic, channel_id=999)

        # 1. Content must ask what animation type and what production issue
        content = consult.get_message_content()
        assert "Animation Studio Consultation" in content
        assert "What type of animation" in content
        assert "What production issue" in content
        assert "Token Bucket" in content
        assert "Burst Spikes" in content

        # 2. Test animation select callback
        mock_anim_interaction = MagicMock()
        mock_anim_interaction.data = {"values": ["leaky_bucket"]}
        mock_anim_interaction.response.defer = AsyncMock()
        await consult.on_select_animation(mock_anim_interaction)
        assert consult.selected_animation == "leaky_bucket"

        # 3. Test issue select callback
        mock_issue_interaction = MagicMock()
        mock_issue_interaction.data = {"values": ["redis_race"]}
        mock_issue_interaction.response.defer = AsyncMock()
        await consult.on_select_issue(mock_issue_interaction)
        assert consult.selected_issue == "redis_race"

        # 4. Test generate video button
        mock_btn_interaction = MagicMock()
        mock_btn_interaction.message.content = "Original Content"
        mock_btn_interaction.response.edit_message = AsyncMock()
        mock_btn_interaction.channel = AsyncMock()

        with patch("src.bot.views.deliver_post_package", new_callable=AsyncMock) as mock_deliver:
            await consult.generate_video_button.callback(mock_btn_interaction)
            mock_btn_interaction.response.edit_message.assert_called_once()
            mock_deliver.assert_called_once()
            call_kwargs = mock_deliver.call_args[1]
            assert call_kwargs["format_type"] == "video"
            assert "Redis" in call_kwargs["custom_hook"] or "race condition" in call_kwargs["custom_hook"]

        # 5. Test custom issue chat button
        mock_chat_interaction = MagicMock()
        mock_chat_interaction.response.send_message = AsyncMock()
        await consult.custom_issue_button.callback(mock_chat_interaction)
        mock_chat_interaction.response.send_message.assert_called_once()
        chat_prompt = mock_chat_interaction.response.send_message.call_args[0][0]
        assert "Tell me your specific setup or issue in chat" in chat_prompt

    asyncio.run(_run())


def test_dynamic_video_resolution_for_all_rate_limiter_algorithms():
    """Verifies that selecting leaky_bucket, fixed_window, or sliding_window delivers their distinct mp4 video files."""
    from src.bot.views import deliver_post_package, CHANNEL_PENDING_APPROVAL

    async def _run():
        rate_topic = next(t for t in TOPIC_POOL if t.id == "rate_limiter")
        mock_channel = AsyncMock()
        mock_channel.id = 777001

        # Test 1: Leaky Bucket delivery
        CHANNEL_PENDING_APPROVAL.pop(mock_channel.id, None)
        await deliver_post_package(
            channel=mock_channel,
            topic=rate_topic,
            angle_content="Leaky Bucket test angle",
            senior_question="Test Q",
            format_type="video",
            animation_id="leaky_bucket"
        )
        assert mock_channel.send.called
        video_call_file = mock_channel.send.call_args_list[0][1]["file"]
        assert "LeakyBucketScene.mp4" in video_call_file.filename
        assert CHANNEL_PENDING_APPROVAL[mock_channel.id]["path"].name == "LeakyBucketScene.mp4"

        # Test 2: Fixed Window delivery
        mock_channel.reset_mock()
        CHANNEL_PENDING_APPROVAL.pop(mock_channel.id, None)
        await deliver_post_package(
            channel=mock_channel,
            topic=rate_topic,
            angle_content="Fixed Window test angle",
            senior_question="Test Q",
            format_type="video",
            animation_id="fixed_window"
        )
        assert mock_channel.send.called
        video_call_file = mock_channel.send.call_args_list[0][1]["file"]
        assert "FixedWindowScene.mp4" in video_call_file.filename
        assert CHANNEL_PENDING_APPROVAL[mock_channel.id]["path"].name == "FixedWindowScene.mp4"

        # Test 3: Sliding Window delivery
        mock_channel.reset_mock()
        CHANNEL_PENDING_APPROVAL.pop(mock_channel.id, None)
        await deliver_post_package(
            channel=mock_channel,
            topic=rate_topic,
            angle_content="Sliding Window test angle",
            senior_question="Test Q",
            format_type="video",
            animation_id="sliding_window"
        )
        assert mock_channel.send.called
        video_call_file = mock_channel.send.call_args_list[0][1]["file"]
        assert "SlidingWindowScene.mp4" in video_call_file.filename
        assert CHANNEL_PENDING_APPROVAL[mock_channel.id]["path"].name == "SlidingWindowScene.mp4"

    asyncio.run(_run())


def test_synchronized_delivery_progress_and_cache_busting():
    """Verifies real synchronized progress updates on progress_msg and unique cache-busting filenames."""
    from src.bot.views import deliver_post_package, CHANNEL_PENDING_APPROVAL

    async def _run():
        rate_topic = next(t for t in TOPIC_POOL if t.id == "rate_limiter")
        mock_channel = AsyncMock()
        mock_channel.id = 777002

        mock_progress_msg = AsyncMock()
        mock_progress_msg.edit = AsyncMock()

        CHANNEL_PENDING_APPROVAL.pop(mock_channel.id, None)
        await deliver_post_package(
            channel=mock_channel,
            topic=rate_topic,
            angle_content="Sliding Window test angle",
            senior_question="Test Q",
            format_type="video",
            animation_id="sliding_window",
            progress_msg=mock_progress_msg
        )

        # 1. progress_msg must have been edited across real lifecycle stages
        assert mock_progress_msg.edit.call_count >= 3
        edit_contents = [call.kwargs.get("content", "") for call in mock_progress_msg.edit.call_args_list]

        # 2. Check strict stage formatting: [1/3], [2/3], [3/3]
        assert any("[1/3]" in c for c in edit_contents)
        assert any("[2/3]" in c for c in edit_contents)
        assert any("[3/3]" in c for c in edit_contents)

        # 3. Check cache-busting filename
        video_call_file = mock_channel.send.call_args_list[0][1]["file"]
        assert video_call_file.filename.startswith("draft_")
        assert "SlidingWindowScene.mp4" in video_call_file.filename

    asyncio.run(_run())






