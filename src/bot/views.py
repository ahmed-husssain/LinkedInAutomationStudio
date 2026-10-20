"""
Discord Interactive UI Views & Components.
Provides mobile-optimized dropdowns, zero-truncation question rendering,
dynamic topic rerolling, and 1-tap post delivery.
"""

import random
import secrets
import asyncio
import time
import re
from typing import List, Optional, Callable
import discord
from discord.ui import Button, View, Select

from src.config.topics import Topic, TOPIC_POOL, get_topic_consultation_data
from src.engines.text_splitter import split_text_for_option
from src.engines.copy_engine import format_linkedin_post
from src.engines.diagram_engine import (
    generate_technical_diagram,
    generate_technical_diagram_async,
    THEMES,
)

from collections import deque
from pathlib import Path
from src.engines.storage_manager import purge_draft, promote_to_published

# In-memory channel state tracker (maps channel_id to last selected Topic)
CHANNEL_ACTIVE_TOPIC = {}

# In-memory channel pending approval lock tracker (maps channel_id to pending draft info)
CHANNEL_PENDING_APPROVAL = {}

# In-memory channel consultation state tracker (maps channel_id to active consultation view & preferences)
CHANNEL_CONSULTATION_STATE = {}

# In-memory recent topic history to prevent repeated suggestions (initialized with 'oauth' to skip previous work)
RECENT_TOPIC_IDS: deque = deque(["oauth"], maxlen=6)



class PostRejectionRecoveryView(View):
    """
    Post-Rejection Feedback & Recovery Router.
    Collects rejection reason and provides 1-tap recovery actions:
    - 🔄 Regenerate with Alternate Hook
    - 🎨 Switch Format / Theme
    - 🎯 Choose Another Topic
    - 🔥 AI Discover Bite-Sized Topics
    """
    def __init__(
        self,
        topic: Optional[Topic] = None,
        prev_angle: str = "",
        prev_q: str = "",
        prev_format: str = "diagram"
    ):
        super().__init__(timeout=600)
        self.topic = topic
        self.prev_angle = prev_angle
        self.prev_q = prev_q
        self.prev_format = prev_format

        options = [
            discord.SelectOption(
                label="Hook wasn't punchy / Too generic",
                value="generic_hook",
                emoji="🎣",
                description="Needs a stronger engineering incident or curiosity hook"
            ),
            discord.SelectOption(
                label="Visual/Diagram style didn't fit",
                value="visual_style",
                emoji="🎨",
                description="Diagram or layout felt cluttered or off-brand"
            ),
            discord.SelectOption(
                label="Topic was too complex / Hard to explain",
                value="too_complex",
                emoji="🧠",
                description="Needs a simpler, more bite-sized mental model"
            ),
            discord.SelectOption(
                label="Wrong format (wanted Video or Carousel)",
                value="wrong_format",
                emoji="📐",
                description="Prefer a different visual presentation"
            ),
            discord.SelectOption(
                label="Just want a fresh regeneration",
                value="reroll",
                emoji="🔄",
                description="Reroll with different angles and phrasing"
            ),
        ]
        select = Select(
            placeholder="💬 What didn't satisfy you with this draft?",
            min_values=1,
            max_values=1,
            options=options,
            row=0
        )
        select.callback = self.feedback_callback
        self.add_item(select)

        rerun_btn = Button(label="🔄 Regenerate (New Hook)", style=discord.ButtonStyle.primary, row=1)
        rerun_btn.callback = self.regenerate_callback
        self.add_item(rerun_btn)

        format_btn = Button(label="🎨 Switch Format", style=discord.ButtonStyle.secondary, row=1)
        format_btn.callback = self.switch_format_callback
        self.add_item(format_btn)

        pick_btn = Button(label="🎯 Pick Another Topic", style=discord.ButtonStyle.secondary, row=2)
        pick_btn.callback = self.pick_topic_callback
        self.add_item(pick_btn)

        ai_btn = Button(label="🔥 AI Discover Bite-Sized Topics", style=discord.ButtonStyle.green, row=2)
        ai_btn.callback = self.ai_discover_callback
        self.add_item(ai_btn)

    def get_message_content(self) -> str:
        topic_name = self.topic.title if self.topic else "this concept"
        return (
            f"🗑️ **Draft Rejected & Purged from Storage.** Zero disk footprint left.\n\n"
            f"🎯 **Let's dial it in for '{topic_name}':**\n"
            f"What was the main reason this didn't satisfy you, and how would you like to proceed?"
        )

    async def feedback_callback(self, interaction: discord.Interaction):
        selected = interaction.data.get("values", [""])[0]
        label_map = {
            "generic_hook": "Hook wasn't punchy / Too generic",
            "visual_style": "Visual/Diagram style didn't fit",
            "too_complex": "Topic was too complex / Hard to explain",
            "wrong_format": "Wrong format (wanted Video or Carousel)",
            "reroll": "Just want a fresh regeneration",
        }
        reason = label_map.get(selected, "Feedback recorded")
        await interaction.response.send_message(
            f"📝 **Feedback Noted:** *\"{reason}\"*\n"
            f"Tap an action below to proceed with the adjusted draft:",
            ephemeral=True
        )

    async def regenerate_callback(self, interaction: discord.Interaction):
        if not self.topic:
            await interaction.response.send_message("No topic active. Please pick a topic.", ephemeral=True)
            return
        await interaction.response.defer()
        next_angle = self.topic.angles[1].text if len(self.topic.angles) > 1 else self.topic.angles[0].text
        next_q = self.topic.questions[1] if len(self.topic.questions) > 1 else self.topic.questions[0]
        CHANNEL_PENDING_APPROVAL[interaction.channel_id] = {"path": None, "type": self.prev_format}
        asyncio.create_task(
            deliver_post_package(
                channel=interaction.channel,
                topic=self.topic,
                angle_content=next_angle,
                senior_question=next_q,
                format_type=self.prev_format
            )
        )

    async def switch_format_callback(self, interaction: discord.Interaction):
        if not self.topic:
            await interaction.response.send_message("No topic active.", ephemeral=True)
            return
        view = TopicConfiguratorView(self.topic)
        await interaction.response.send_message(content=view.get_message_content(), view=view, ephemeral=False)

    async def pick_topic_callback(self, interaction: discord.Interaction):
        view = TopicSelectionView()
        await interaction.response.send_message(content=view.get_message_content(), view=view, ephemeral=False)

    async def ai_discover_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        from src.agents.strategist import ContentStrategistAgent
        strategist = ContentStrategistAgent()
        trending = strategist.discover_trending_topics(count=3)
        cards = [
            f"**{i}️⃣ {t.get('title', 'Topic')}**\n• *Why it works:* {t.get('tagline', '')}\n• *Incident Hook:* \"{t.get('hook', '')}\""
            for i, t in enumerate(trending, 1)
        ]
        from src.bot.views import TrendingTopicsActionView
        action_view = TrendingTopicsActionView(trending)
        await interaction.channel.send(
            content=f"🔥 **Top 1% Bite-Sized Visual Architecture Topics:**\n\n" + "\n\n".join(cards) + "\n\n👉 *Tap below to generate for Topic #1 or choose format:*",
            view=action_view
        )


class PostApprovalView(View):
    """
    Approval Gate View: Locks the channel until user Approves or Rejects the delivered draft.
    """
    def __init__(
        self,
        channel_id: int,
        file_path: Optional[Path] = None,
        post_text: str = "",
        topic: Optional[Topic] = None,
        angle_content: str = "",
        senior_question: str = "",
        format_type: str = "diagram"
    ):
        super().__init__(timeout=86400) # 24h expiration
        self.channel_id = channel_id
        self.file_path = Path(file_path) if file_path else None
        self.post_text = post_text
        self.topic = topic
        self.angle_content = angle_content
        self.senior_question = senior_question
        self.format_type = format_type

    @discord.ui.button(label="Approve & Post to LinkedIn", style=discord.ButtonStyle.green, emoji="🚀", row=0)
    async def approve_button(self, interaction: discord.Interaction, button: Button):
        CHANNEL_PENDING_APPROVAL.pop(self.channel_id, None)
        if self.file_path and self.file_path.exists():
            promote_to_published(self.file_path)

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            content=interaction.message.content + "\n\n✅ **Approved & Ready!** Draft promoted to vault. Channel unlocked.",
            view=self
        )

    @discord.ui.button(label="Reject & Discard", style=discord.ButtonStyle.danger, emoji="❌", row=0)
    async def reject_button(self, interaction: discord.Interaction, button: Button):
        CHANNEL_PENDING_APPROVAL.pop(self.channel_id, None)
        if self.file_path:
            purge_draft(self.file_path)

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            content=interaction.message.content + "\n\n🗑️ **Draft Rejected & Discarded.** Zero disk trace left. Channel unlocked.",
            view=self
        )

        # Launch Post-Rejection Recovery Flow
        if hasattr(interaction, "channel") and interaction.channel:
            recovery_view = PostRejectionRecoveryView(
                topic=self.topic,
                prev_angle=self.angle_content,
                prev_q=self.senior_question,
                prev_format=self.format_type
            )
            try:
                await interaction.channel.send(
                    content=recovery_view.get_message_content(),
                    view=recovery_view
                )
            except Exception:
                pass

    async def on_timeout(self):
        CHANNEL_PENDING_APPROVAL.pop(self.channel_id, None)
        if self.file_path:
            purge_draft(self.file_path)


class AnimationConsultationView(View):
    """
    Animation Studio Consultation View.
    Prompts the user to specify their desired animation mechanism and production issue
    before generating the video animation and LinkedIn post.
    """
    def __init__(self, topic: Topic, channel_id: int):
        super().__init__(timeout=600)
        self.topic = topic
        self.channel_id = channel_id
        self.data = get_topic_consultation_data(topic)

        self.selected_animation = self.data["animations"][0]["id"]
        self.selected_issue = self.data["issues"][0]["id"]

        # 1. Animation Mechanism Select Menu
        anim_options = [
            discord.SelectOption(
                label=a["label"][:100],
                value=a["id"],
                description=a["desc"][:100],
                default=(a["id"] == self.selected_animation)
            )
            for a in self.data["animations"][:5]
        ]
        self.anim_select = Select(
            placeholder="Select Animation / Algorithm Type",
            options=anim_options,
            row=0
        )
        self.anim_select.callback = self.on_select_animation
        self.add_item(self.anim_select)

        # 2. Production Issue Select Menu
        issue_options = [
            discord.SelectOption(
                label=i["label"][:100],
                value=i["id"],
                description=i["desc"][:100],
                default=(i["id"] == self.selected_issue)
            )
            for i in self.data["issues"][:5]
        ]
        self.issue_select = Select(
            placeholder="Select Production Issue / Bottleneck",
            options=issue_options,
            row=1
        )
        self.issue_select.callback = self.on_select_issue
        self.add_item(self.issue_select)

    def get_message_content(self) -> str:
        anim_bullets = "\n".join(
            f"• **{a['label']}:** {a['desc']}"
            for a in self.data["animations"]
        )
        issue_bullets = "\n".join(
            f"• **{i['label']}:** {i['desc']}"
            for i in self.data["issues"]
        )

        return (
            f"**Animation Studio Consultation: {self.data.get('title', self.topic.title)}**\n\n"
            f"Before generating your video animation and LinkedIn post, select your parameters:\n\n"
            f"**1. What type of animation / algorithm mechanism do you want to show?**\n"
            f"{anim_bullets}\n\n"
            f"**2. What production issue or bottleneck are you facing?**\n"
            f"{issue_bullets}\n\n"
            f"Choose from the menus below or reply directly in chat with your custom setup."
        )

    async def on_select_animation(self, interaction: discord.Interaction):
        if interaction.data and interaction.data.get("values"):
            self.selected_animation = interaction.data["values"][0]
            for opt in self.anim_select.options:
                opt.default = (opt.value == self.selected_animation)
        try:
            await interaction.response.defer()
        except Exception:
            pass

    async def on_select_issue(self, interaction: discord.Interaction):
        if interaction.data and interaction.data.get("values"):
            self.selected_issue = interaction.data["values"][0]
            for opt in self.issue_select.options:
                opt.default = (opt.value == self.selected_issue)
        try:
            await interaction.response.defer()
        except Exception:
            pass

    @discord.ui.button(label="Generate Post & Video", style=discord.ButtonStyle.primary, row=2)
    async def generate_video_button(self, interaction: discord.Interaction, button: Button):
        issue_obj = next((i for i in self.data["issues"] if i["id"] == self.selected_issue), self.data["issues"][0])
        anim_obj = next((a for a in self.data["animations"] if a["id"] == self.selected_animation), self.data["animations"][0])

        custom_hook = issue_obj.get("hook", "")
        angle_content = issue_obj.get("angle", f"• Focus: {anim_obj['label']}\n• Challenge: {issue_obj['desc']}")
        senior_q = issue_obj.get("question", self.topic.questions[0])

        for child in self.children:
            child.disabled = True

        status_text = (
            f"[{anim_obj['label']} | {issue_obj['label']}]\n"
            f"[1/3] Validating parameters and consultation inputs..."
        )

        try:
            await interaction.response.edit_message(
                content=status_text,
                view=self
            )
        except Exception:
            pass

        CHANNEL_CONSULTATION_STATE.pop(self.channel_id, None)

        target_channel = interaction.channel if hasattr(interaction, "channel") and interaction.channel else None
        if target_channel:
            await deliver_post_package(
                channel=target_channel,
                topic=self.topic,
                angle_content=angle_content,
                senior_question=senior_q,
                format_type="video",
                custom_hook=custom_hook,
                animation_id=self.selected_animation,
                progress_msg=interaction.message
            )

    @discord.ui.button(label="Generate Carousel Instead", style=discord.ButtonStyle.secondary, row=2)
    async def generate_carousel_button(self, interaction: discord.Interaction, button: Button):
        issue_obj = next((i for i in self.data["issues"] if i["id"] == self.selected_issue), self.data["issues"][0])
        anim_obj = next((a for a in self.data["animations"] if a["id"] == self.selected_animation), self.data["animations"][0])

        custom_hook = issue_obj.get("hook", "")
        angle_content = issue_obj.get("angle", f"• Focus: {anim_obj['label']}\n• Challenge: {issue_obj['desc']}")
        senior_q = issue_obj.get("question", self.topic.questions[0])

        for child in self.children:
            child.disabled = True

        status_text = (
            f"[{anim_obj['label']} | {issue_obj['label']}]\n"
            f"[1/3] Validating parameters and slide structure..."
        )

        try:
            await interaction.response.edit_message(
                content=status_text,
                view=self
            )
        except Exception:
            pass

        CHANNEL_CONSULTATION_STATE.pop(self.channel_id, None)

        target_channel = interaction.channel if hasattr(interaction, "channel") and interaction.channel else None
        if target_channel:
            await deliver_post_package(
                channel=target_channel,
                topic=self.topic,
                angle_content=angle_content,
                senior_question=senior_q,
                format_type="carousel",
                custom_hook=custom_hook,
                progress_msg=interaction.message
            )

    @discord.ui.button(label="Custom Issue (Chat)", style=discord.ButtonStyle.secondary, row=2)
    async def custom_issue_button(self, interaction: discord.Interaction, button: Button):
        try:
            await interaction.response.send_message(
                "Tell me your specific setup or issue in chat:\n"
                "(e.g. \"Our payment gateway gets flooded when 5,000 users checkout at once and Redis Lua locks up\")\n\n"
                "I will generate the technical post and animation tailored to your bottleneck.",
                ephemeral=True
            )
        except Exception:
            pass


async def deliver_post_package(
    channel: discord.TextChannel,
    topic: Topic,
    angle_content: str,
    senior_question: str,
    format_type: str = "video",
    custom_hook: Optional[str] = None,
    animation_id: Optional[str] = None,
    progress_msg: Optional[discord.Message] = None
):
    """
    Renders and sends the complete LinkedIn package to the Discord channel
    with synchronized step updates and unique cache-busting filenames.
    """
    async def _update_progress(step: int, total: int, text: str):
        if progress_msg:
            try:
                await progress_msg.edit(content=f"[{step}/{total}] {text}")
            except Exception:
                pass

    post_text = format_linkedin_post(
        topic_title=topic.title,
        subject=topic.subject or topic.title,
        angle_content=angle_content,
        senior_question=senior_question,
        custom_hook=custom_hook
    )

    file_base = topic.id.replace("_", " ").title().replace(" ", "")
    unique_id = int(time.time())
    generated_path: Optional[Path] = None

    try:
        if format_type == "video":
            await _update_progress(1, 3, f"Validating parameters for {topic.title}...")
            from src.engines.video_engine import resolve_video_path

            video_path = None
            chosen_filename = None

            if animation_id:
                video_path = resolve_video_path(animation_id)
                if video_path:
                    chosen_filename = video_path.name
            elif topic.video_filename:
                video_path = resolve_video_path(topic.video_filename)
                if video_path:
                    chosen_filename = video_path.name

            if not video_path and topic.video_path and topic.video_path.exists():
                video_path = topic.video_path
                chosen_filename = topic.video_path.name

            if not video_path or not video_path.exists():
                CHANNEL_PENDING_APPROVAL.pop(channel.id, None)
                await _update_progress(2, 3, f"[ERROR] Animation asset for {animation_id or topic.title} could not be resolved.")
                await channel.send(
                    f"**Video Generation Error:** Animation asset for `{animation_id or topic.title}` could not be resolved.\n"
                    f"*No silent fallback was served to protect technical accuracy.*"
                )
                return

            await _update_progress(2, 3, f"Compiling video animation asset ({chosen_filename})...")
            generated_path = Path(video_path)
            v_file = discord.File(str(video_path), filename=f"draft_{unique_id}_{chosen_filename}")

            await _update_progress(3, 3, "Staging LinkedIn draft package and thumbnail...")

            approval_view = PostApprovalView(
                channel_id=channel.id,
                file_path=generated_path,
                post_text=post_text,
                topic=topic,
                angle_content=angle_content,
                senior_question=senior_question,
                format_type=format_type
            )
            CHANNEL_PENDING_APPROVAL[channel.id] = {
                "path": generated_path,
                "type": format_type,
                "view": approval_view
            }

            await channel.send(
                content=(
                    f"**YOUR READY-TO-POST LINKEDIN PACKAGE**\n"
                    f"────────────────────────────────────────\n"
                    f"{post_text}\n"
                    f"────────────────────────────────────────\n"
                    f"1. Copy post copy above\n"
                    f"2. Video player attached below:\n\n"
                    f"**APPROVAL GATE:** Tap 'Approve' to post, or 'Reject' to discard and clean up:"
                ),
                file=v_file,
                view=approval_view
            )

            # Standalone thumbnail
            thumb_path = topic.thumb_path or generate_technical_diagram(topic.id, topic.title, topic.tagline)
            if thumb_path and thumb_path.exists():
                t_file = discord.File(str(thumb_path), filename=f"thumb_{unique_id}_{file_base}.png")
                await channel.send(
                    content="**Custom 1080x1080 Video Thumbnail** *(Save to use as cover on LinkedIn)*:",
                    file=t_file
                )
            await _update_progress(3, 3, "Complete: Draft package ready for review.")
        elif format_type == "carousel":
            await _update_progress(1, 3, f"Validating slide structure for {topic.title}...")
            from src.agents.carousel_builder import build_pdf_carousel
            slides_data = []
            for idx, a in enumerate(topic.angles):
                lines = [line.strip().lstrip("• ") for line in a.text.split("\n") if line.strip()]
                slides_data.append({
                    "badge": f"Concept {idx+1}",
                    "title": a.label[:32],
                    "subtitle": a.desc[:50] if a.desc else topic.tagline[:50],
                    "bullets": lines[:3],
                    "accent": "#58a6ff" if idx == 0 else "#bc8cff"
                })
            slides_data.append({
                "badge": "Key Takeaway",
                "title": "Production Rule",
                "subtitle": "Engineering Best Practice",
                "bullets": [
                    f"Never deploy {topic.subject or topic.title} without latency metrics.",
                    "Enforce strict timeouts and circuit breaker patterns.",
                    "Verify failure modes under simulated peak traffic."
                ],
                "accent": "#3fb950"
            })
            await _update_progress(2, 3, "Compiling multi-slide PDF carousel...")
            pdf_path = build_pdf_carousel(
                topic_id=topic.id,
                topic_title=topic.title,
                slides_data=slides_data,
                senior_question=senior_question
            )
            await _update_progress(3, 3, "Staging carousel draft package...")
            generated_path = Path(pdf_path)
            pdf_file = discord.File(str(pdf_path), filename=f"draft_{unique_id}_{file_base}_Carousel.pdf")

            approval_view = PostApprovalView(
                channel_id=channel.id,
                file_path=generated_path,
                post_text=post_text,
                topic=topic,
                angle_content=angle_content,
                senior_question=senior_question,
                format_type=format_type
            )
            CHANNEL_PENDING_APPROVAL[channel.id] = {
                "path": generated_path,
                "type": format_type,
                "view": approval_view
            }

            await channel.send(
                content=(
                    f"**YOUR READY-TO-POST LINKEDIN PACKAGE**\n"
                    f"────────────────────────────────────────\n"
                    f"{post_text}\n"
                    f"────────────────────────────────────────\n"
                    f"**Interactive 1080x1350 PDF Carousel attached below** *(Upload as 'Document' on LinkedIn for 3x reach)*:\n\n"
                    f"**APPROVAL GATE:** Tap 'Approve' to post, or 'Reject' to discard and clean up:"
                ),
                file=pdf_file,
                view=approval_view
            )
            await _update_progress(3, 3, "Complete: Carousel draft ready for review.")
        else:
            # Technical architecture diagram delivery
            await _update_progress(1, 3, f"Validating diagram parameters for {topic.title}...")
            from src.engines.storage_manager import DRAFTS_DIR
            await _update_progress(2, 3, "Rendering high-fidelity architecture diagram...")
            thumb_path = await generate_technical_diagram_async(
                topic.id,
                topic.title,
                topic.tagline,
                output_dir=DRAFTS_DIR,
                overwrite=True
            )
            await _update_progress(3, 3, "Staging diagram draft package...")
            generated_path = Path(thumb_path)
            t_file = discord.File(str(thumb_path), filename=f"draft_{unique_id}_{file_base}_Diagram.png")

            approval_view = PostApprovalView(
                channel_id=channel.id,
                file_path=generated_path,
                post_text=post_text,
                topic=topic,
                angle_content=angle_content,
                senior_question=senior_question,
                format_type=format_type
            )
            CHANNEL_PENDING_APPROVAL[channel.id] = {
                "path": generated_path,
                "type": format_type,
                "view": approval_view
            }

            await channel.send(
                content=(
                    f"**YOUR READY-TO-POST LINKEDIN PACKAGE**\n"
                    f"────────────────────────────────────────\n"
                    f"{post_text}\n"
                    f"────────────────────────────────────────\n"
                    f"Technical diagram attached below:\n\n"
                    f"**APPROVAL GATE:** Tap 'Approve' to post, or 'Reject' to discard and clean up:"
                ),
                file=t_file,
                view=approval_view
            )
            await _update_progress(3, 3, "Complete: Diagram draft ready for review.")
    except Exception as e:
        CHANNEL_PENDING_APPROVAL.pop(channel.id, None)
        await _update_progress(1, 3, f"[ERROR] Generation failed: {e}")
        await channel.send(f"**Generation Error:** {e}. Channel lock released.")
        raise


class TopicConfiguratorView(View):
    """Mobile-optimized configuration view for angles, questions, and format."""
    def __init__(self, topic: Topic, q_offset: int = 0, selected_q: Optional[str] = None):
        super().__init__(timeout=600)
        self.topic = topic
        self.q_offset = q_offset
        all_q = topic.questions
        self.active_questions = [all_q[(q_offset + i) % len(all_q)] for i in range(min(3, len(all_q)))]

        self.selected_angle = topic.angles[0].text
        self.selected_q = selected_q
        self.has_chosen_question = selected_q is not None

        # 1. Angle dropdown
        angle_options = []
        for i, a in enumerate(topic.angles):
            l1, l2 = split_text_for_option(a.label, max_line1=38, max_line2=95)
            if not l2 and a.desc:
                l2 = a.desc[:95]
            angle_options.append(
                discord.SelectOption(
                    label=l1,
                    description=l2,
                    value=f"angle_{i}"
                )
            )
        self.angle_select = Select(placeholder="🎯 1. Choose what to focus on...", options=angle_options, row=0)
        self.angle_select.callback = self.on_angle_change
        self.add_item(self.angle_select)

        # 2. Question dropdown (Full text visible across 2 lines without truncation)
        number_emojis = ["1️⃣", "2️⃣", "3️⃣"]
        q_options = []
        for i, q in enumerate(self.active_questions):
            l1, l2 = split_text_for_option(q, max_line1=38, max_line2=95)
            q_options.append(
                discord.SelectOption(
                    label=l1,
                    description=l2,
                    value=f"q_{i}",
                    emoji=number_emojis[i] if i < len(number_emojis) else "❓"
                )
            )
        self.q_select = Select(
            placeholder="💬 2. Choose Discussion Question to Unlock Formats...",
            options=q_options,
            row=1
        )
        self.q_select.callback = self.on_q_change
        self.add_item(self.q_select)

        # 3. Delivery format buttons (Disabled until question is explicitly chosen!)
        if topic.has_video:
            self.video_btn = Button(
                label="🎬 Short Video (10-15s) + Thumbnail",
                style=discord.ButtonStyle.primary,
                emoji="🎥",
                row=2,
                disabled=not self.has_chosen_question
            )
            self.video_btn.callback = self.make_format_callback("video")
            self.add_item(self.video_btn)
        else:
            self.video_btn = None

        self.pdf_btn = Button(
            label="📑 6-Slide PDF Carousel",
            style=discord.ButtonStyle.success,
            emoji="📄",
            row=2,
            disabled=not self.has_chosen_question
        )
        self.pdf_btn.callback = self.make_format_callback("carousel")
        self.add_item(self.pdf_btn)

        self.img_btn = Button(
            label="🖼️ Technical Architecture Diagram",
            style=discord.ButtonStyle.secondary,
            emoji="📊",
            row=2,
            disabled=not self.has_chosen_question
        )
        self.img_btn.callback = self.make_format_callback("image")
        self.add_item(self.img_btn)

        # 4. Reroll questions button
        reroll_q_btn = Button(
            label="🔄 Different Questions",
            style=discord.ButtonStyle.secondary,
            emoji="❓",
            row=3
        )
        reroll_q_btn.callback = self.reroll_questions_callback
        self.add_item(reroll_q_btn)

    def get_message_content(self) -> str:
        number_emojis = ["1️⃣", "2️⃣", "3️⃣"]
        q_text = "\n".join([f"{number_emojis[i]} *\"{q}\"*" for i, q in enumerate(self.active_questions)])

        if self.has_chosen_question and self.selected_q:
            return (
                f"📌 **TOPIC:** **{self.topic.title}**\n"
                f"*{self.topic.tagline}*\n\n"
                f"✅ **CHOSEN DISCUSSION QUESTION:**\n"
                f"💬 *\"{self.selected_q}\"*\n\n"
                f"🚀 **STEP 3 OF 3: Choose Your Generation Format**\n"
                f"────────────────────────────────────────\n"
                f"• 🎬 **Short Video:** 10-15s animated MP4 (60fps) + cover thumbnail\n"
                f"• 📑 **6-Slide PDF Carousel:** 1080x1350 multi-page mobile document deck\n"
                f"• 🖼️ **Architecture Diagram:** 1080x1080 high-contrast technical card\n"
                f"────────────────────────────────────────\n"
                f"👉 Tap an active format button below to generate:"
            )
        else:
            return (
                f"📌 **TOPIC:** **{self.topic.title}**\n"
                f"*{self.topic.tagline}*\n\n"
                f"💬 **STEP 2 OF 3: Choose a Senior Discussion Question**\n"
                f"────────────────────────────────────────\n"
                f"{q_text}\n"
                f"────────────────────────────────────────\n"
                f"👉 **Action:** Pick which question you want to debate using the dropdown menu below.\n"
                f"*(The generation buttons below will unlock once you pick your question)*"
            )

    async def reroll_questions_callback(self, interaction: discord.Interaction):
        new_offset = (self.q_offset + 3) % len(self.topic.questions)
        new_view = TopicConfiguratorView(self.topic, new_offset)
        await interaction.response.edit_message(
            content=new_view.get_message_content(),
            view=new_view
        )

    async def on_angle_change(self, interaction: discord.Interaction):
        CHANNEL_ACTIVE_TOPIC[interaction.channel_id] = self.topic
        idx = int(self.angle_select.values[0].split("_")[1])
        self.selected_angle = self.topic.angles[idx].text
        await interaction.response.defer()

    async def on_q_change(self, interaction: discord.Interaction):
        CHANNEL_ACTIVE_TOPIC[interaction.channel_id] = self.topic
        idx = int(self.q_select.values[0].split("_")[1])
        self.selected_q = self.active_questions[idx]
        self.has_chosen_question = True

        # Unlock format buttons
        if self.video_btn:
            self.video_btn.disabled = False
        self.pdf_btn.disabled = False
        self.img_btn.disabled = False

        await interaction.response.edit_message(
            content=self.get_message_content(),
            view=self
        )

    def make_format_callback(self, format_type: str):
        async def callback(interaction: discord.Interaction):
            CHANNEL_ACTIVE_TOPIC[interaction.channel_id] = self.topic
            if not self.has_chosen_question or not self.selected_q:
                await interaction.response.send_message(
                    "⚠️ **Please choose a discussion question from the dropdown first before generating!**",
                    ephemeral=True
                )
                return

            if interaction.channel_id in CHANNEL_PENDING_APPROVAL:
                await interaction.response.send_message(
                    "⚠️ **Action Blocked:** You have an active draft awaiting review in this channel!\n\n"
                    "👉 *Please tap **'🚀 Approve & Post'** or **'❌ Reject & Discard'** on the draft above first before generating a new asset (or type `!unlock` to reset).* ",
                    ephemeral=True
                )
                return

            if format_type == "video":
                from src.bot.views import AnimationConsultationView, CHANNEL_CONSULTATION_STATE
                consult_view = AnimationConsultationView(topic=self.topic, channel_id=interaction.channel_id)
                CHANNEL_CONSULTATION_STATE[interaction.channel_id] = {
                    "topic": self.topic,
                    "view": consult_view
                }
                await interaction.response.send_message(
                    content=consult_view.get_message_content(),
                    view=consult_view
                )
                return

            # Lock immediately to prevent double-clicks
            CHANNEL_PENDING_APPROVAL[interaction.channel_id] = {"path": None, "type": format_type}

            await interaction.response.defer()
            asyncio.create_task(
                deliver_post_package(
                    interaction.channel,
                    self.topic,
                    self.selected_angle,
                    self.selected_q,
                    format_type
                )
            )
        return callback


class TopicSelectionView(View):
    """Main topic browser with guaranteed fresh dynamic rerolling and anti-repeat history."""
    def __init__(self, topics: Optional[List[Topic]] = None):
        super().__init__(timeout=600)
        if topics:
            self.current_topics = topics
        else:
            # Filter out recently worked-on topics (e.g. OAuth) so they are NEVER repeatedly suggested
            eligible = [t for t in TOPIC_POOL if t.id not in RECENT_TOPIC_IDS]
            if len(eligible) < 3:
                # If pool exhausted, only exclude the most recent one
                eligible = [t for t in TOPIC_POOL if t.id != (RECENT_TOPIC_IDS[-1] if RECENT_TOPIC_IDS else "")]
                if len(eligible) < 3:
                    eligible = TOPIC_POOL
            self.current_topics = secrets.SystemRandom().sample(eligible, min(3, len(eligible)))

        for i, t in enumerate(self.current_topics):
            btn = Button(label=f"{i+1}. {t.title[:25]}", style=discord.ButtonStyle.green, row=i)
            btn.callback = self.make_callback(t)
            self.add_item(btn)

        reroll_btn = Button(label="🔄 Reroll Topics", style=discord.ButtonStyle.secondary, row=3)
        reroll_btn.callback = self.reroll_callback
        self.add_item(reroll_btn)

        ai_btn = Button(label="🔥 AI Viral Topics", style=discord.ButtonStyle.primary, row=3)
        ai_btn.callback = self.ai_discover_callback
        self.add_item(ai_btn)

    def get_message_content(self) -> str:
        topics_text = "\n".join([f"**{i+1}️⃣ {t.title}**\n   *{t.tagline}*" for i, t in enumerate(self.current_topics)])
        return (
            f"🚀 **LinkedIn Automation Studio**\n\n"
            f"🎯 **STEP 1 OF 3: Choose a System Design Topic**\n"
            f"────────────────────────────────────────\n"
            f"{topics_text}\n"
            f"────────────────────────────────────────\n"
            f"👉 **Action:** Tap a topic button below, or type any custom topic name in chat:\n"
            f"*(Tap '🔄 Reroll Topics' for fresh ideas, or '🔥 AI Viral Topics' for real-time trending angles)*"
        )

    def make_callback(self, topic: Topic):
        async def callback(interaction: discord.Interaction):
            RECENT_TOPIC_IDS.append(topic.id)
            CHANNEL_ACTIVE_TOPIC[interaction.channel_id] = topic
            config_view = TopicConfiguratorView(topic)
            await interaction.response.send_message(
                content=config_view.get_message_content(),
                view=config_view,
                ephemeral=False
            )
        return callback

    async def reroll_callback(self, interaction: discord.Interaction):
        # Pick 3 topics STRICTLY from those NOT currently displayed and NOT recently used
        current_ids = {t.id for t in self.current_topics}
        excluded_ids = current_ids.union(set(RECENT_TOPIC_IDS))
        remaining = [t for t in TOPIC_POOL if t.id not in excluded_ids]
        if len(remaining) < 3:
            remaining = [t for t in TOPIC_POOL if t.id not in current_ids]
            if len(remaining) < 3:
                remaining = TOPIC_POOL

        new_topics = secrets.SystemRandom().sample(remaining, min(3, len(remaining)))
        new_view = TopicSelectionView(new_topics)
        await interaction.response.edit_message(
            content=new_view.get_message_content(),
            view=new_view
        )

    async def ai_discover_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        from src.agents.strategist import ContentStrategistAgent
        strategist = ContentStrategistAgent()
        trending = strategist.discover_trending_topics(count=3)
        cards = []
        for i, t in enumerate(trending, 1):
            cards.append(
                f"**{i}️⃣ {t.get('title', 'Architecture Topic')}**\n"
                f"• *Why it works:* {t.get('tagline', '')}\n"
                f"• *Incident Hook:* \"{t.get('hook', '')}\""
            )
        formatted = "\n\n".join(cards)
        action_view = TrendingTopicsActionView(trending)
        await interaction.channel.send(
            content=(
                f"🔥 **AI-Discovered Viral Production Topics:**\n\n"
                f"{formatted}\n\n"
                f"👉 *Tap a button below to generate a video or carousel for Topic #1, or discover more:*"
            ),
            view=action_view
        )


class TrendingTopicsActionView(View):
    """Interactive view for AI-discovered trending topics with 1-tap generation buttons."""
    def __init__(self, topics: List[dict]):
        super().__init__(timeout=600)
        self.topics = topics
        first = topics[0] if topics else {}
        first_title = first.get("title", "Topic #1")
        short_title = first_title[:20]

        vid_btn = Button(
            label=f"🎬 Video: {short_title}",
            style=discord.ButtonStyle.primary,
            row=0
        )
        vid_btn.callback = self.make_video_callback(first)
        self.add_item(vid_btn)

        pdf_btn = Button(
            label=f"📑 Carousel: {short_title}",
            style=discord.ButtonStyle.success,
            row=0
        )
        pdf_btn.callback = self.make_pdf_callback(first)
        self.add_item(pdf_btn)

        reroll_btn = Button(
            label="🔄 Discover 3 More AI Topics",
            style=discord.ButtonStyle.secondary,
            row=1
        )
        reroll_btn.callback = self.reroll_callback
        self.add_item(reroll_btn)

    def make_pdf_callback(self, topic_data: dict):
        async def callback(interaction: discord.Interaction):
            if not topic_data:
                await interaction.response.send_message("No topic data.", ephemeral=True)
                return
            await interaction.response.defer()
            title = topic_data.get("title", "Distributed Architecture")
            status_msg = await interaction.channel.send(
                f"🚀 **Building High-Retention PDF Carousel for: {title}...**\n"
                f"• Brainstorming 6 visual slides with Content Strategist...\n"
                f"• Compiling 1080x1350 dark-mode document with Carousel Architect..."
            )
            import re
            from src.agents.strategist import ContentStrategistAgent
            from src.agents.carousel_builder import build_pdf_carousel
            from src.engines.copy_engine import format_linkedin_post
            strategist = ContentStrategistAgent()
            draft = strategist.brainstorm_topic(title)
            slug = re.sub(r"[^a-zA-Z0-9_]", "_", title.lower())
            pdf_path = build_pdf_carousel(
                topic_id=slug,
                topic_title=draft.get("topic_title", title),
                slides_data=draft.get("slides", []),
                senior_question=draft.get("senior_question", "")
            )
            post_copy = format_linkedin_post(
                topic_title=draft.get("topic_title", title),
                subject=draft.get("subject", title),
                angle_content=draft.get("body", ""),
                senior_question=draft.get("senior_question", "")
            )
            pdf_file = discord.File(str(pdf_path), filename=f"{slug}_Carousel.pdf")
            await status_msg.edit(
                content=(
                    f"✅ **YOUR 6-SLIDE PDF CAROUSEL IS READY!**\n"
                    f"────────────────────────────────────────\n"
                    f"{post_copy}\n"
                    f"────────────────────────────────────────\n"
                    f"📑 **Interactive PDF Document attached below:**"
                )
            )
            await interaction.channel.send(file=pdf_file)
        return callback

    def make_video_callback(self, topic_data: dict):
        async def callback(interaction: discord.Interaction):
            if not topic_data:
                await interaction.response.send_message("No topic data.", ephemeral=True)
                return
            await interaction.response.defer()
            title = topic_data.get("title", "Distributed Architecture")
            slug = re.sub(r"[^a-zA-Z0-9_]", "_", title.lower())
            thumb_path = await generate_technical_diagram_async(slug, title, topic_data.get("tagline", ""))
            post_copy = format_linkedin_post(
                topic_title=title,
                subject=title,
                angle_content=topic_data.get("hook", ""),
                senior_question="How does your team handle this in production?"
            )
            t_file = discord.File(str(thumb_path), filename=f"{slug}_Cover.png")
            await interaction.channel.send(
                content=(
                    f"🎉 **YOUR READY-TO-POST LINKEDIN PACKAGE**\n"
                    f"────────────────────────────────────────\n"
                    f"{post_copy}\n"
                    f"────────────────────────────────────────\n"
                    f"🖼️ **Technical 1080x1080 Cover Diagram attached below:**"
                ),
                file=t_file
            )
        return callback

    async def reroll_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        from src.agents.strategist import ContentStrategistAgent
        strategist = ContentStrategistAgent()
        new_trending = strategist.discover_trending_topics(count=3)
        cards = []
        for i, t in enumerate(new_trending, 1):
            cards.append(
                f"**{i}️⃣ {t.get('title', 'Architecture Topic')}**\n"
                f"• *Why it works:* {t.get('tagline', '')}\n"
                f"• *Incident Hook:* \"{t.get('hook', '')}\""
            )
        formatted = "\n\n".join(cards)
        new_view = TrendingTopicsActionView(new_trending)
        await interaction.channel.send(
            content=(
                f"🔄 **Fresh AI-Discovered Production Topics:**\n\n"
                f"{formatted}\n\n"
                f"👉 *Tap a button below to generate:* "
            ),
            view=new_view
        )


class ThumbnailThemeView(View):
    """Allows choosing from 4 color palettes for instant thumbnail generation."""
    def __init__(self, topic: Topic):
        super().__init__(timeout=600)
        self.topic = topic
        theme_items = [
            ("🔵 Cyan High-Contrast", "cyan"),
            ("🟢 Emerald Dark", "emerald"),
            ("🟣 Neon Purple", "purple"),
            ("🟡 Warm Amber", "amber"),
        ]
        for label, theme_key in theme_items:
            btn = Button(label=label, style=discord.ButtonStyle.secondary)
            btn.callback = self.make_callback(theme_key)
            self.add_item(btn)

    def make_callback(self, theme_key: str):
        async def callback(interaction: discord.Interaction):
            await interaction.response.defer()
            img_path = await generate_technical_diagram_async(
                self.topic.id,
                self.topic.title,
                self.topic.tagline,
                theme=theme_key,
                overwrite=True
            )
            file = discord.File(str(img_path), filename=f"{self.topic.id}_{theme_key}.png")
            await interaction.channel.send(
                content=f"🎨 **Custom {theme_key.title()} cover image for '{self.topic.title}':**",
                file=file
            )
        return callback


class QuickActionView(View):
    """Contextual response view when user sends freeform text messages."""
    def __init__(self, topic: Topic):
        super().__init__(timeout=600)
        self.topic = topic

        cfg_btn = Button(label=f"🎯 Configure '{topic.title[:20]}'", style=discord.ButtonStyle.primary)
        cfg_btn.callback = self.on_cfg
        self.add_item(cfg_btn)

        thm_btn = Button(label="🎨 Change Thumbnail", style=discord.ButtonStyle.secondary)
        thm_btn.callback = self.on_thm
        self.add_item(thm_btn)

        topics_btn = Button(label="🚀 Browse All Topics", style=discord.ButtonStyle.success)
        topics_btn.callback = self.on_topics
        self.add_item(topics_btn)

    async def on_cfg(self, interaction: discord.Interaction):
        view = TopicConfiguratorView(self.topic)
        await interaction.response.send_message(
            content=view.get_message_content(),
            view=view
        )

    async def on_thm(self, interaction: discord.Interaction):
        view = ThumbnailThemeView(self.topic)
        await interaction.response.send_message(
            content=f"🎨 **Select a thumbnail theme for '{self.topic.title}':**",
            view=view
        )

    async def on_topics(self, interaction: discord.Interaction):
        view = TopicSelectionView()
        topics_text = "\n".join([f"• **{t.title}** — *{t.tagline}*" for t in view.current_topics])
        await interaction.response.send_message(
            content=f"👋 **Here are fresh topics:**\n\n{topics_text}\n\n👉 *Tap one below to configure:*",
            view=view
        )
