"""
REST Poller & Natural Language Dispatcher.
Features bounded-memory message deduplication (LRU), regex mention stripping,
and priority-based keyword matching without false positives.
"""

import re
import asyncio
from collections import deque
from typing import Set, Tuple, Optional, Dict
import discord

from src.config.settings import MESSAGE_CACHE_MAX_SIZE
from src.config.topics import TOPIC_POOL, Topic, get_topic_by_id
from src.bot.views import (
    TopicConfiguratorView,
    TopicSelectionView,
    ThumbnailThemeView,
    QuickActionView,
    CHANNEL_ACTIVE_TOPIC,
    RECENT_TOPIC_IDS,
    CHANNEL_PENDING_APPROVAL,
)
from src.engines.storage_manager import purge_draft


class BoundedMessageTracker:
    """Bounded-memory LRU message ID tracker to prevent memory leaks in 24/7 runs."""
    def __init__(self, max_size: int = MESSAGE_CACHE_MAX_SIZE):
        self.max_size = max(10, max_size)
        self._deque: deque = deque(maxlen=self.max_size)
        self._set: Set[int] = set()

    def add(self, message_id: int) -> bool:
        """
        Adds message_id. Returns True if was already seen (duplicate), False if newly added.
        """
        if message_id in self._set:
            return True

        # If deque reached max capacity, the oldest item will be evicted
        if len(self._deque) == self._deque.maxlen:
            oldest = self._deque[0]
            self._set.discard(oldest)

        self._deque.append(message_id)
        self._set.add(message_id)
        return False

    def __contains__(self, message_id: int) -> bool:
        return message_id in self._set

    def __len__(self) -> int:
        return len(self._set)


# Global tracker instance
message_tracker = BoundedMessageTracker(MESSAGE_CACHE_MAX_SIZE)


def clean_discord_mentions(raw_text: str, bot_name: str = "") -> str:
    """Strips user mentions, role mentions, channel tags, bot names, and invisible chars."""
    if not raw_text:
        return ""

    # Strip user & role mentions: <@123>, <@!123>, <@&123>, channel tags <#123>
    cleaned = re.sub(r"<[@#][!&]?\d+>", "", raw_text)

    # Strip bot names with optional leading '@' using word boundaries
    names_to_remove = ["LinkedIn Studio"]
    if bot_name:
        names_to_remove.append(bot_name)

    for name in names_to_remove:
        escaped = re.escape(name)
        cleaned = re.sub(rf"@?{escaped}\b", "", cleaned, flags=re.IGNORECASE)

    # Strip unprintable control characters and zero-width spaces
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\u200b-\u200f\ufeff]", "", cleaned)

    return " ".join(cleaned.strip().split())


def match_user_intent(clean_text: str, current_topic: Topic) -> Dict:
    """
    Parses intent from cleaned text with strict word-boundary matching to prevent
    false positive substring collisions (e.g. 'hi' inside 'this').
    """
    lower = clean_text.lower()

    # 0. Emergency Unlock / Reset command
    if re.search(r"^(!?(unlock|reset|clear_lock))$", lower.strip()):
        return {"intent": "UNLOCK"}

    # 1. Message Queue keyword matching (high priority)
    if re.search(r"\b(queues?|rabbitmq|sqs|kafka|buffer)\b", lower):
        topic = get_topic_by_id("message_queues")
        if topic:
            return {"intent": "TOPIC_MATCH", "topic": topic}

    # 2. General Topic Pool Match (Exact id or full title match)
    for t in TOPIC_POOL:
        if t.id == lower or t.title.lower() == lower:
            return {"intent": "TOPIC_MATCH", "topic": t}

    # Match specific domain keywords with word boundaries
    keyword_map = [
        (r"\b(oauth|oauth2|pkce)\b", "oauth"),
        (r"\b(rate\s*limit|token\s*bucket)\b", "rate_limiter"),
        (r"\b(sql\s*index|b-?tree)\b", "sql_index"),
        (r"\b(idempotenc\w*|duplicate\s*charge)\b", "api_idempotency"),
        (r"\b(cache-?aside|redis\s*cache)\b", "cache_aside"),
        (r"\b(sharding|partitioning)\b", "sharding_partitioning"),
        (r"\b(websockets?|long\s*polling)\b", "websockets_polling"),
        (r"\b(jwts?|server\s*sessions?)\b", "jwt_vs_sessions"),
        (r"\b(connection\s*pool\w*|pgbouncer)\b", "connection_pooling"),
        (r"\b(optimistic\s*lock\w*|pessimistic\s*lock\w*)\b", "optimistic_locking"),
        (r"\b(bloom\s*filter\w*)\b", "bloom_filters"),
        (r"\b(circuit\s*breaker\w*)\b", "circuit_breaker"),
    ]
    for pattern, tid in keyword_map:
        if re.search(pattern, lower):
            topic = get_topic_by_id(tid)
            if topic:
                return {"intent": "TOPIC_MATCH", "topic": topic}

    # 2b. Conversational topic suggestions / discovery queries -> Route to Multi-Agent Orchestrator
    if re.search(r"\b(trending|fresh|interesting|better|suggest\w*|ideas?|old\s*built-?in|viral|feedback|video\s*or\s*pdf|more\s*topics?)\b", lower):
        return {"intent": "FALLBACK"}

    # 2c. Direct Format Generation Request for Current Active Topic
    if re.search(r"\b(video(\s*animation)?|animat\w*|make\s*a?\s*video|generate\s*video|create\s*video|show\s*video)\b", lower):
        return {"intent": "GENERATE_ACTIVE_FORMAT", "format": "video"}
    if re.search(r"\b(carousel|deck|pdf\s*carousel|slides?|make\s*a?\s*carousel|generate\s*carousel)\b", lower):
        return {"intent": "GENERATE_ACTIVE_FORMAT", "format": "carousel"}
    if re.search(r"\b(diagram|architecture(\s*diagram)?|2d\s*image|cover\s*diagram|make\s*diagram)\b", lower):
        return {"intent": "GENERATE_ACTIVE_FORMAT", "format": "diagram"}

    # 3. Customization: Thumbnail / Cover / Theme
    if re.search(r"\b(thumbs?|thumbnails?|covers?|themes?|images?|art)\b", lower):
        return {"intent": "THUMBNAIL_OPTIONS"}

    # 4. Simpler Explanation
    if re.search(r"\b(confusing|simpler?|simple|easy|beginner|explain|understand)\b", lower):
        return {"intent": "SIMPLIFY"}

    # 5. Different Question
    if re.search(r"\b(questions?|seniors?|discussions?|different\s*question)\b", lower):
        return {"intent": "DIFFERENT_QUESTIONS"}

    # 7. Explicit Menu / Daily / Browse command
    if re.search(r"^(!?(start|menu|topics?|daily|help)|browse\s*topics?|show\s*topics?|list\s*topics?)$", lower.strip()):
        return {"intent": "BROWSE_TOPICS"}
    if re.search(r"\b(menu|browse\s*topics?|show\s*topics?|list\s*topics?)\b", lower) and len(clean_text.split()) <= 4:
        return {"intent": "BROWSE_TOPICS"}

    # 8. Fallback Conversation (includes greetings, questions, custom requests)
    return {"intent": "FALLBACK"}


async def dispatch_user_message(
    channel: discord.TextChannel,
    author: discord.User,
    raw_text: str,
    bot_name: str = "LinkedIn Studio",
    message: Optional[discord.Message] = None
):
    """Processes cleaned text and sends the appropriate interactive response."""
    clean_text = clean_discord_mentions(raw_text, bot_name)
    if not clean_text:
        return

    channel_id = channel.id
    current_topic = CHANNEL_ACTIVE_TOPIC.get(channel_id)
    if not current_topic:
        eligible = [t for t in TOPIC_POOL if t.id not in RECENT_TOPIC_IDS]
        current_topic = eligible[0] if eligible else TOPIC_POOL[0]

    parsed = match_user_intent(clean_text, current_topic)
    intent = parsed["intent"]

    # Helper for replying inline if message is present, or falling back to channel.send
    async def reply_or_send(content: str, view: Optional[discord.ui.View] = None):
        if message:
            try:
                if view:
                    return await message.reply(content=content, view=view, mention_author=True)
                return await message.reply(content=content, mention_author=True)
            except discord.DiscordException:
                pass
        if view:
            return await channel.send(content=content, view=view)
        return await channel.send(content=content)

    if intent == "UNLOCK":
        pending = CHANNEL_PENDING_APPROVAL.pop(channel_id, None)
        if pending and pending.get("path"):
            purge_draft(pending["path"])
            await reply_or_send("🔓 **Channel unlocked!** Pending draft was purged and storage cleaned up.")
        else:
            await reply_or_send("🔓 **Channel is already unlocked!** No pending drafts found.")
        return

    # Check if channel is locked awaiting approval
    if channel_id in CHANNEL_PENDING_APPROVAL and intent in ("TOPIC_MATCH", "BROWSE_TOPICS", "THUMBNAIL_OPTIONS", "SIMPLIFY", "DIFFERENT_QUESTIONS", "GENERATE_ACTIVE_FORMAT"):
        await reply_or_send(
            "⚠️ **Action Blocked:** You have a pending draft awaiting your review in this channel!\n\n"
            "👉 *Please tap **'🚀 Approve & Post'** or **'❌ Reject & Discard'** on the draft above first, or type `!unlock` to reset.*"
        )
        return

    if intent == "TOPIC_MATCH":
        matched = parsed["topic"]
        CHANNEL_ACTIVE_TOPIC[channel_id] = matched
        view = TopicConfiguratorView(matched)
        await reply_or_send(
            content=f"🎯 **Found Topic:** **{matched.title}**\n\n{view.get_message_content()}",
            view=view
        )

    elif intent == "GENERATE_ACTIVE_FORMAT":
        req_format = parsed["format"]
        if req_format == "video" and not current_topic.has_video:
            await reply_or_send(
                content=(
                    f"🎬 **Topic '{current_topic.title}' does not have a pre-rendered 60fps MP4 video.**\n\n"
                    f"Would you like to generate the **Interactive PDF Carousel** or the **Technical Architecture Diagram**?"
                ),
                view=TopicConfiguratorView(current_topic)
            )
            return

        CHANNEL_PENDING_APPROVAL[channel_id] = {"path": None, "type": req_format}
        from src.bot.views import deliver_post_package
        asyncio.create_task(
            deliver_post_package(
                channel=channel,
                topic=current_topic,
                angle_content=current_topic.angles[0].text,
                senior_question=current_topic.questions[0],
                format_type=req_format
            )
        )

    elif intent == "BROWSE_TOPICS":
        view = TopicSelectionView()
        await reply_or_send(
            content=view.get_message_content(),
            view=view
        )

    elif intent == "THUMBNAIL_OPTIONS":
        await reply_or_send(
            content=(
                f"🎨 **Thumbnail Options for '{current_topic.title}':**\n"
                f"Pick a color theme below to generate a new 1080x1080 cover thumbnail right on your phone:"
            ),
            view=ThumbnailThemeView(current_topic)
        )

    elif intent == "SIMPLIFY":
        simple_angle = current_topic.angles[0].text
        await reply_or_send(
            content=(
                f"💡 **Simpler Step-by-Step Breakdown for '{current_topic.title}':**\n\n"
                f"{simple_angle}\n\n"
                f"👉 *Tap below to configure and generate this post:* "
            ),
            view=TopicConfiguratorView(current_topic)
        )

    elif intent == "DIFFERENT_QUESTIONS":
        new_view = TopicConfiguratorView(current_topic, q_offset=1)
        await reply_or_send(
            content=f"🔄 **Here are different discussion questions for '{current_topic.title}':**\n\n{new_view.get_message_content()}",
            view=new_view
        )

    else:
        # Freeform conversational prompt -> Dispatch to Gemini Multi-Agent Studio!
        if message:
            try:
                from src.agents.orchestrator import AgentStudioOrchestrator
                orchestrator = AgentStudioOrchestrator()
                asyncio.create_task(orchestrator.handle_conversational_request(message, clean_text))
            except Exception as e:
                print(f"Error dispatching conversational request: {e}", flush=True)
                await reply_or_send(
                    content=f"🤖 **Hey {author.mention}!** I received your message: *\"{clean_text}\"*\nTap below to explore options:",
                    view=QuickActionView(current_topic)
                )
        else:
            await reply_or_send(
                content=(
                    f"🤖 **Hey {author.mention}! Got your message:** *\"{clean_text}\"*\n\n"
                    f"Here is what you can do directly from your phone:\n"
                    f"• Type any topic name (e.g. **oauth**, **kafka**, **rate limiter**, **idempotency**)\n"
                    f"• Ask me to generate a post (e.g. **\"Break down Redis Sentinel vs Cluster\"**)\n"
                    f"• Type **\"topics\"** to browse all recommendations\n\n"
                    f"Or tap an action below:"
                ),
                view=QuickActionView(current_topic)
            )
