"""
Discord Interactive UI Views & Components.
Provides mobile-optimized dropdowns, zero-truncation question rendering,
dynamic topic rerolling, and 1-tap post delivery.
"""

import random
import asyncio
from typing import List, Optional, Callable
import discord
from discord.ui import Button, View, Select

from src.config.topics import Topic, TOPIC_POOL
from src.engines.text_splitter import split_text_for_option
from src.engines.copy_engine import format_linkedin_post
from src.engines.diagram_engine import generate_technical_diagram, THEMES

# In-memory channel state tracker (maps channel_id to last selected Topic)
CHANNEL_ACTIVE_TOPIC = {}


async def deliver_post_package(
    channel: discord.TextChannel,
    topic: Topic,
    angle_content: str,
    senior_question: str,
    format_type: str = "video"
):
    """
    Renders and sends the complete LinkedIn package to the Discord channel
    within 2 seconds: formatted post copy, playable video, and custom 1080x1080 thumbnail.
    """
    post_text = format_linkedin_post(
        topic_title=topic.title,
        subject=topic.subject or topic.title,
        angle_content=angle_content,
        senior_question=senior_question
    )

    file_base = topic.id.replace("_", " ").title().replace(" ", "")

    # Video delivery
    if format_type == "video" and topic.has_video:
        video_path = topic.video_path
        v_file = discord.File(str(video_path), filename=f"{file_base}Animation.mp4")

        await channel.send(
            content=(
                f"🎉 **YOUR READY-TO-POST LINKEDIN PACKAGE**\n"
                f"────────────────────────────────────────\n"
                f"{post_text}\n"
                f"────────────────────────────────────────\n"
                f"👉 *1. Copy post copy above*\n"
                f"👉 *2. Video player attached below:*"
            ),
            file=v_file
        )

        # Standalone thumbnail
        thumb_path = topic.thumb_path or generate_technical_diagram(topic.id, topic.title, topic.tagline)
        if thumb_path and thumb_path.exists():
            t_file = discord.File(str(thumb_path), filename=f"{file_base}Thumbnail.png")
            await channel.send(
                content="🖼️ **Custom 1080x1080 Video Thumbnail** *(Save to camera roll to use as cover on LinkedIn)*:",
                file=t_file
            )
    elif format_type == "carousel":
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
        pdf_path = build_pdf_carousel(
            topic_id=topic.id,
            topic_title=topic.title,
            slides_data=slides_data,
            senior_question=senior_question
        )
        pdf_file = discord.File(str(pdf_path), filename=f"{file_base}_Carousel.pdf")
        await channel.send(
            content=(
                f"🎉 **YOUR READY-TO-POST LINKEDIN PACKAGE**\n"
                f"────────────────────────────────────────\n"
                f"{post_text}\n"
                f"────────────────────────────────────────\n"
                f"📑 **Interactive 1080x1350 PDF Carousel attached below** *(Upload as 'Document' on LinkedIn for 3x reach)*:"
            ),
            file=pdf_file
        )
    else:
        # Technical architecture diagram delivery
        thumb_path = topic.thumb_path or generate_technical_diagram(topic.id, topic.title, topic.tagline)
        t_file = discord.File(str(thumb_path), filename=f"{file_base}Diagram.png")
        await channel.send(
            content=(
                f"🎉 **YOUR READY-TO-POST LINKEDIN PACKAGE**\n"
                f"────────────────────────────────────────\n"
                f"{post_text}\n"
                f"────────────────────────────────────────\n"
                f"👉 *Technical diagram attached below:*"
            ),
            file=t_file
        )


class TopicConfiguratorView(View):
    """Mobile-optimized configuration view for angles, questions, and format."""
    def __init__(self, topic: Topic, q_offset: int = 0):
        super().__init__(timeout=600)
        self.topic = topic
        self.q_offset = q_offset
        all_q = topic.questions
        self.active_questions = [all_q[(q_offset + i) % len(all_q)] for i in range(min(3, len(all_q)))]

        self.selected_angle = topic.angles[0].text
        self.selected_q = self.active_questions[0]

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
            placeholder="💬 2. Choose Discussion Question...",
            options=q_options,
            row=1
        )
        self.q_select.callback = self.on_q_change
        self.add_item(self.q_select)

        # 3. Delivery format buttons
        if topic.has_video:
            video_btn = Button(
                label="🎬 Short Video (10-15s) + Thumbnail",
                style=discord.ButtonStyle.primary,
                emoji="🎥",
                row=2
            )
            video_btn.callback = self.make_format_callback("video")
            self.add_item(video_btn)

        pdf_btn = Button(
            label="📑 6-Slide PDF Carousel",
            style=discord.ButtonStyle.success,
            emoji="📄",
            row=2
        )
        pdf_btn.callback = self.make_format_callback("carousel")
        self.add_item(pdf_btn)

        img_btn = Button(
            label="🖼️ Technical Architecture Diagram",
            style=discord.ButtonStyle.secondary,
            emoji="📊",
            row=2
        )
        img_btn.callback = self.make_format_callback("image")
        self.add_item(img_btn)

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
        return (
            f"📌 **TOPIC:** **{self.topic.title}**\n"
            f"*{self.topic.tagline}*\n\n"
            f"💬 **Senior Discussion Questions (Full Text):**\n"
            f"{q_text}\n\n"
            f"👉 *Select the question from the dropdown below (or tap '🔄 Different Questions'):*"
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
        await interaction.response.defer()

    def make_format_callback(self, format_type: str):
        async def callback(interaction: discord.Interaction):
            CHANNEL_ACTIVE_TOPIC[interaction.channel_id] = self.topic
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
    """Main topic browser with guaranteed fresh dynamic rerolling."""
    def __init__(self, topics: Optional[List[Topic]] = None):
        super().__init__(timeout=600)
        if topics:
            self.current_topics = topics
        else:
            # Default presentation: pick 3 randomized topics from the full pool
            self.current_topics = random.sample(TOPIC_POOL, min(3, len(TOPIC_POOL)))

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

    def make_callback(self, topic: Topic):
        async def callback(interaction: discord.Interaction):
            CHANNEL_ACTIVE_TOPIC[interaction.channel_id] = topic
            config_view = TopicConfiguratorView(topic)
            await interaction.response.send_message(
                content=config_view.get_message_content(),
                view=config_view,
                ephemeral=False
            )
        return callback

    async def reroll_callback(self, interaction: discord.Interaction):
        # Pick 3 topics STRICTLY from those NOT currently displayed
        current_ids = {t.id for t in self.current_topics}
        remaining = [t for t in TOPIC_POOL if t.id not in current_ids]
        if len(remaining) < 3:
            remaining = TOPIC_POOL

        new_topics = random.sample(remaining, min(3, len(remaining)))
        new_view = TopicSelectionView(new_topics)
        topic_list_text = "\n".join([f"• **{t.title}** — *{t.tagline}*" for t in new_topics])
        await interaction.response.edit_message(
            content=(
                f"🔄 **Here are 3 fresh topics:**\n\n"
                f"{topic_list_text}\n\n"
                f"👉 *Tap one below to configure options:* "
            ),
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
            from src.engines.diagram_engine import generate_technical_diagram
            from src.engines.copy_engine import format_linkedin_post
            import re
            slug = re.sub(r"[^a-zA-Z0-9_]", "_", title.lower())
            thumb_path = generate_technical_diagram(slug, title, topic_data.get("tagline", ""))
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
            img_path = generate_technical_diagram(
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
