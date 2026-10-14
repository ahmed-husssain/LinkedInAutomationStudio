"""
Discord Studio Bot Client & Lifecycle Runner.
Integrates event listeners, REST background polling, commands,
and resilient gateway auto-reconnection.
"""

import os
import sys
import time
import asyncio
import discord
from discord.ext import commands, tasks

from src.config.settings import DISCORD_BOT_TOKEN, DISCORD_POLL_INTERVAL_SECONDS
from src.config.topics import TOPIC_POOL
from src.bot.views import TopicSelectionView
from src.bot.poller import message_tracker, dispatch_user_message

# Bot setup with privileged message_content intent enabled for real-time natural language interaction
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command(name="daily", aliases=["topics", "start", "menu"])
async def cmd_daily_topics(ctx):
    """Interactive command to display the daily recommended topics menu."""
    view = TopicSelectionView()
    topics_text = "\n".join([f"• **{t.title}** — *{t.tagline}*" for t in view.current_topics])
    await ctx.send(
        f"👋 **Good morning! Here are today's recommended topics:**\n\n"
        f"{topics_text}\n\n"
        f"Tap a button to configure options:",
        view=view
    )


@tasks.loop(seconds=DISCORD_POLL_INTERVAL_SECONDS)
async def poll_channel_messages():
    """Background REST poller for guilds without gateway message content intent."""
    for guild in bot.guilds:
        for channel in guild.text_channels:
            perms = channel.permissions_for(guild.me)
            if not perms.read_messages or not perms.send_messages:
                continue

            try:
                async for msg in channel.history(limit=5):
                    if msg.author.bot:
                        continue

                    raw_content = (msg.clean_content or msg.content or "").strip()
                    if not raw_content:
                        continue

                    # Check deduplication cache
                    if msg.id in message_tracker:
                        continue
                    message_tracker.add(msg.id)

                    await dispatch_user_message(channel, msg.author, raw_content, bot.user.name, message=msg)
            except (discord.DiscordException, OSError):
                # Silently catch transient channel read errors
                pass


@bot.event
async def on_message(message: discord.Message):
    """Processes messages delivered via gateway event."""
    if message.author.bot:
        return

    raw_content = (message.clean_content or message.content or "").strip()
    if not raw_content:
        return

    # Check deduplication cache
    if message.id in message_tracker:
        return
    message_tracker.add(message.id)

    await dispatch_user_message(message.channel, message.author, raw_content, bot.user.name if bot.user else "", message=message)
    await bot.process_commands(message)


@tasks.loop(hours=24)
async def daily_autonomous_publisher():
    """Daily autonomous studio autopilot: delivers ready-to-review package every morning."""
    for guild in bot.guilds:
        target_channel = next((c for c in guild.text_channels if c.name == "general"), None)
        if not target_channel and guild.text_channels:
            target_channel = guild.text_channels[0]

        if target_channel and target_channel.permissions_for(guild.me).send_messages:
            topic = TOPIC_POOL[0]
            from src.bot.views import TopicConfiguratorView
            view = TopicConfiguratorView(topic)
            try:
                await target_channel.send(
                    content=(
                        f"🌅 **Good Morning! Daily Studio Autopilot Active:**\n"
                        f"Today's recommended topic: **{topic.title}**\n\n"
                        f"{view.get_message_content()}"
                    ),
                    view=view
                )
            except discord.DiscordException:
                pass


@bot.event
async def on_ready():
    """Triggered when Discord gateway connects successfully."""
    print(f"🤖 LinkedIn Studio Bot is online as {bot.user} (ID: {bot.user.id})!", flush=True)
    if not poll_channel_messages.is_running():
        poll_channel_messages.start()
        print(f"⚡ Background REST Poller active (interval: {DISCORD_POLL_INTERVAL_SECONDS}s)", flush=True)
    if not daily_autonomous_publisher.is_running():
        daily_autonomous_publisher.start()
        print(f"⏰ Daily Studio Autopilot loop initialized (24h cadence)", flush=True)


def run_bot(token: str = None):
    """Starts the bot with infinite auto-reconnection on network interruptions."""
    bot_token = (token or DISCORD_BOT_TOKEN).strip()
    if not bot_token:
        print("❌ Error: DISCORD_BOT_TOKEN is missing. Please set it in .env file.", file=sys.stderr)
        sys.exit(1)

    print("🚀 Launching LinkedIn Automation Studio Discord Bot...", flush=True)
    retry_delay = 5
    while True:
        try:
            bot.run(bot_token)
        except KeyboardInterrupt:
            print("\n👋 Bot shut down by user.", flush=True)
            break
        except Exception as e:
            print(f"⚠️ Gateway Disconnect: {e}. Reconnecting in {retry_delay}s...", flush=True)
            time.sleep(retry_delay)
            retry_delay = min(60, retry_delay * 2)


if __name__ == "__main__":
    run_bot()
