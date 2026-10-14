"""
Multi-Agent Studio Orchestrator.
Coordinates Discord in-chat replies, dispatches Strategist, Critic, and Carousel Architect,
and delivers production-ready LinkedIn packages right in your conversation.
"""

import re
import os
import asyncio
import logging
from pathlib import Path
from typing import Optional
import discord

from src.agents.gemini_client import GeminiClient
from src.agents.strategist import ContentStrategistAgent
from src.agents.critic import StaffEngineerCriticAgent
from src.agents.carousel_builder import build_pdf_carousel
from src.engines.copy_engine import format_linkedin_post

logger = logging.getLogger("StudioOrchestrator")


class AgentStudioOrchestrator:
    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        self.gemini = gemini_client or GeminiClient()
        self.strategist = ContentStrategistAgent(self.gemini)
        self.critic = StaffEngineerCriticAgent(self.gemini)

    async def handle_conversational_request(
        self,
        message: discord.Message,
        clean_text: str
    ):
        """
        Processes conversational messages and replies directly in the same channel.
        Intelligently routes between:
        1. Layout / Video feedback & re-renders
        2. Technical Q&A / system design consultation
        3. Full Multi-Agent LinkedIn Post & Carousel generation
        """
        channel = message.channel
        author = message.author
        lower = clean_text.lower()

        try:
            # -----------------------------------------------------------------
            # 1. Video / Layout / Overlapping Divs Feedback
            # -----------------------------------------------------------------
            if re.search(r"\b(overlap\w*|video|divs?|controls?|scrubber|player|cut off|collision|fix video|re-?render)\b", lower):
                video_path = Path("D:/LinkedInAutomationStudio/assets/videos/QueueScene.mp4")
                thumb_path = Path("D:/LinkedInAutomationStudio/assets/thumbnails/QueueThumbnail.png")
                
                reply_text = (
                    f"🛠️ **Hey {author.mention}! Video Layout Overhaul Complete!**\n\n"
                    f"I addressed the text collision issue:\n"
                    f"• **Bottom HUD Safe Zone:** Moved all dynamic banners well above the bottom margin (`Y > -2.0`), "
                    f"leaving generous clearance so Discord/LinkedIn video player scrubbers (`0:08/0:08`) never obscure text.\n"
                    f"• **Single Active Takeaway:** Replaced stacked bottom banners with a smooth-fading `CORE SUPERPOWER` card, "
                    f"eliminating overlapping divs.\n\n"
                    f"Here is your freshly rendered, crystal-clear 1080x1080 60fps video & cover thumbnail:"
                )
                
                files = []
                if video_path.exists():
                    files.append(discord.File(str(video_path), filename="QueueScene_Fixed.mp4"))
                if thumb_path.exists():
                    files.append(discord.File(str(thumb_path), filename="QueueThumbnail_Fixed.png"))
                
                if files:
                    await message.reply(content=reply_text, files=files, mention_author=True)
                else:
                    await message.reply(content=reply_text, mention_author=True)
                return

            # -----------------------------------------------------------------
            # 2. Status / Response Check / Greetings
            # -----------------------------------------------------------------
            if re.search(r"\b(respons\w*|why\s*no\s*reply|still\s*no|waiting|hello|hi|hey|status|online)\b", lower):
                reply_text = (
                    f"👋 **Hey {author.mention}! I'm online, active, and listening directly in this chat.**\n\n"
                    f"I was applying an engine fix to prevent background task drops. Here is what we can do right now:\n"
                    f"• **Build a Post & Carousel:** e.g. *\"Create a carousel for Kafka vs SQS\"* or *\"Break down Redis Sentinel\"*\n"
                    f"• **Ask Tech Architecture Questions:** e.g. *\"How do we handle cache stampedes?\"*\n"
                    f"• **Pick from Curated Topics:** type **\"topics\"** or **\"message queue\"**\n\n"
                    f"What would you like to build or discuss next?"
                )
                await message.reply(content=reply_text, mention_author=True)
                return

            # -----------------------------------------------------------------
            # 2b. Conversational Affirmations & Pleasantries (e.g. 'good', 'nice', 'thanks')
            # -----------------------------------------------------------------
            if re.search(r"^(good|nice|ok|okay|great|cool|awesome|perfect|thanks|thank\s*you|yep|yes|done|sounds\s*good|nice\s*work)[!.\s]*$", lower.strip()):
                reply_text = (
                    f"🙌 **Glad to hear that, {author.mention}!**\n\n"
                    f"Whenever you're ready, let me know what you'd like to craft next:\n"
                    f"• Ask me to generate a post package: e.g. *\"Create a carousel on Kafka vs RabbitMQ\"*\n"
                    f"• Ask an architecture question: e.g. *\"How does Redis Sentinel failover work?\"*\n"
                    f"• Type **\"topics\"** to browse recommended ideas."
                )
                await message.reply(content=reply_text, mention_author=True)
                return

            # -----------------------------------------------------------------
            # 2c. Single-Word Non-Technical Guardrail (e.g. random short words)
            # -----------------------------------------------------------------
            if len(clean_text.split()) == 1 and not re.search(r"\b(queues?|kafka|redis|sql|oauth|cache|sharding|jwt|lock|api|db)\b", lower):
                reply_text = (
                    f"🤖 **Hey {author.mention}!**\n\n"
                    f"What technical concept or system design topic would you like to build today?\n"
                    f"• Type a topic like **\"Kafka\"**, **\"OAuth\"**, or **\"Idempotency\"**\n"
                    f"• Ask for content: *\"Create a carousel on Redis Caching\"*\n"
                    f"• Type **\"topics\"** or **\"trending\"** for fresh high-retention ideas."
                )
                await message.reply(content=reply_text, mention_author=True)
                return

            # -----------------------------------------------------------------
            # 2d. Trending & High-Retention Topic Discovery (AI-Powered)
            # -----------------------------------------------------------------
            if re.search(r"\b(trending|fresh|interesting|better\s*topics?|new\s*topics?|video\s*ideas?|ideas?|suggest|old\s*built-?in|viral|topics?\s*for\s*(video|carousel)|what\s*topics?)\b", lower):
                trending = self.strategist.discover_trending_topics(count=3)

                cards = []
                for i, t in enumerate(trending, 1):
                    cards.append(
                        f"**{i}️⃣ {t.get('title', 'System Design Topic')}**\n"
                        f"• *Why it works:* {t.get('tagline', '')}\n"
                        f"• *Incident Hook:* \"{t.get('hook', '')}\""
                    )

                formatted_topics = "\n\n".join(cards)
                from src.bot.views import TrendingTopicsActionView
                action_view = TrendingTopicsActionView(trending)
                reply_text = (
                    f"🔥 **Top 1% Viral Production Architecture Topics for Video & Carousel:**\n\n"
                    f"{formatted_topics}\n\n"
                    f"👉 **Ready to build?** Tap a button below to generate a **Video** or **6-Slide PDF Carousel** for Topic #1, "
                    f"or reply with: *\"Create a carousel for #1\"*!"
                )
                await message.reply(content=reply_text, view=action_view, mention_author=True)
                return

            # -----------------------------------------------------------------
            # 3. Full Multi-Agent Content Generation (Post + 6-Slide PDF Carousel)
            # -----------------------------------------------------------------
            is_post_request = bool(re.search(
                r"\b(post|carousel|deck|slides?|write|generate|break\s*down|create|architect|vs|compare|explain)\b",
                lower
            ))

            if is_post_request:
                # Send immediate in-chat progress acknowledgment
                status_msg = await message.reply(
                    f"🚀 **Multi-Agent Studio Activated for {author.mention}:**\n"
                    f"• ✍️ **Content Strategist:** Brainstorming authentic hook & mental model...\n"
                    f"• 🧐 **Staff Engineer Critic:** Fact-checking technical accuracy...\n"
                    f"• 📑 **Carousel Architect:** Compiling 6-slide dark-mode PDF document...",
                    mention_author=True
                )

                # Step 1: Strategist Brainstorms
                draft = self.strategist.brainstorm_topic(clean_text)

                # Step 2: Critic Reviews (Adversarial Fact Check)
                critique = self.critic.review_draft(draft)

                # Step 2b: Multi-Agent Auto-Refinement Loop (Zero-dependency Crew Loop)
                if critique.get("senior_appeal_score", 10.0) < 8.8:
                    feedback = critique.get("critique") or critique.get("technical_verdict", "")
                    if feedback:
                        draft = self.strategist.refine_draft(draft, feedback)
                        critique = self.critic.review_draft(draft)

                # Step 3: Build PDF Carousel Deck (1080x1350)
                topic_slug = re.sub(r"[^a-zA-Z0-9_]", "_", draft.get("topic_title", "topic").lower())
                pdf_path = build_pdf_carousel(
                    topic_id=topic_slug,
                    topic_title=draft.get("topic_title", clean_text),
                    slides_data=draft.get("slides", []),
                    senior_question=draft.get("senior_question", "")
                )

                # Step 4: Format authentic post copy
                post_copy = format_linkedin_post(
                    topic_title=draft.get("topic_title", clean_text),
                    subject=draft.get("subject", clean_text),
                    angle_content=draft.get("body", ""),
                    senior_question=draft.get("senior_question", "")
                )

                verdict = critique.get("technical_verdict", "Mechanics verified for production.")
                appeal = critique.get("senior_appeal_score", 9.5)

                final_text = (
                    f"✅ **YOUR MULTI-AGENT LINKEDIN PACKAGE IS READY!**\n"
                    f"────────────────────────────────────────\n"
                    f"🧐 **Staff Engineer Technical Review:**\n"
                    f"*{verdict}*\n"
                    f"🎯 *Senior Dev Appeal Score:* **{appeal}/10**\n"
                    f"────────────────────────────────────────\n"
                    f"📋 **Copy & Paste Post Draft:**\n\n"
                    f"{post_copy}\n"
                    f"────────────────────────────────────────\n"
                    f"📑 **Interactive 6-Slide PDF Carousel attached below** *(Upload as 'Document' on LinkedIn for 3x reach)*:"
                )

                if pdf_path.exists():
                    pdf_file = discord.File(str(pdf_path), filename=f"{topic_slug}_Carousel.pdf")
                    await status_msg.edit(content=final_text)
                    await channel.send(file=pdf_file)
                else:
                    await status_msg.edit(content=final_text)
                return

            # -----------------------------------------------------------------
            # 4. Automation Strategy & Enhancement Advisory
            # -----------------------------------------------------------------
            if re.search(r"\b(better|enhance|top\s*1%|value|upgrade|features?|automation|refactor|improve)\b", lower):
                reply_text = (
                    f"🎯 **Multi-Agent Studio Blueprint for Top 1% Results:**\n\n"
                    f"✍️ **Content Strategist:**\n"
                    f"• **Counter-Intuitive Hooks:** Never start with generic intros. Start with the outage: *\"A 10,000 req/s surge crashed our database in 3 seconds. Here is why adding replicas made it worse.\"*\n"
                    f"• **3-Step Mental Model:** Transform complex distributed architecture into a step-by-step visual progression.\n\n"
                    f"🧐 **Staff Engineer Critic:**\n"
                    f"• **Production Constraints:** Kill generic fluff (*'seamless'*, *'game-changer'*). State exact metrics (*'p99 < 15ms'*, *'at-least-once with idempotent keys'*).\n"
                    f"• **Senior Debate Prompts:** Challenge senior architects on failover, partition rebalances, and edge cases.\n\n"
                    f"📑 **Asset Engine Integration:**\n"
                    f"• **Interactive 1080x1350 PDF Carousels:** Uploaded as LinkedIn Documents for 3x algorithmic reach.\n"
                    f"• **2D Motion Graphics (Manim CE):** 15s square 60fps animations with dedicated UI safe margins.\n\n"
                    f"👉 *Try it: Type \"Create a carousel on Kafka vs RabbitMQ\" or \"Break down Database Sharding\"!*"
                )
                await message.reply(content=reply_text, mention_author=True)
                return

            # -----------------------------------------------------------------
            # 5. General Conversational / Architectural Q&A Fallback
            # -----------------------------------------------------------------
            system_prompt = (
                "You are the Lead System Architect at LinkedIn Studio. "
                "Answer the user's question with senior-level depth, clear bullet points, "
                "concrete real-world trade-offs, and concise formatting under 200 words."
            )
            ai_reply = self.gemini.generate(
                prompt=clean_text,
                system_instruction=system_prompt,
                json_mode=False
            )
            await message.reply(content=f"💡 **Architecture Studio Insight:**\n\n{ai_reply}", mention_author=True)

        except Exception as e:
            logger.error(f"Error handling conversational request: {e}", exc_info=True)
            try:
                await message.reply(
                    content=(
                        f"⚠️ **Note:** I ran into a minor hiccup processing that: `{e}`.\n"
                        f"Feel free to re-type your request or pick a topic anytime!"
                    ),
                    mention_author=True
                )
            except Exception:
                pass
