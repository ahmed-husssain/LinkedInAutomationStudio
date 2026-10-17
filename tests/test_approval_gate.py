"""
Unit and Adversarial Tests for Approval Gate Lock & Lifecycle State Machine.
Verifies channel locking, double-click rejection, approval vault promotion,
rejection instant purge, timeout auto-eviction, and emergency unlock.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
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

