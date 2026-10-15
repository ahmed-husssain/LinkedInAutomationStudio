# 📘 Complete End-to-End Setup & User Guide

Welcome! This step-by-step guide walks you through setting up and running **LinkedIn Automation Studio** from scratch. Even if you have never created a Discord bot or worked with AI APIs before, you will be able to follow this guide from start to finish in about 15 minutes.

---

## 📋 Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Step 1: Discord Bot Setup (Developer Portal)](#step-1-discord-bot-setup-developer-portal)
3. [Step 2: Google Gemini API Key Setup](#step-2-google-gemini-api-key-setup)
4. [Step 3: LinkedIn API Setup (Optional)](#step-3-linkedin-api-setup-optional)
5. [Step 4: Clone the Code & Install Dependencies](#step-4-clone-the-code--install-dependencies)
6. [Step 5: Configure Environment Variables (.env)](#step-5-configure-environment-variables-env)
7. [Step 6: Run Tests & Launch the Bot](#step-6-run-tests--launch-the-bot)
8. [Step 7: How to Use the Studio in Discord](#step-7-how-to-use-the-studio-in-discord)
9. [Troubleshooting & FAQ](#troubleshooting--faq)

---

## 1. Prerequisites

Before starting, ensure you have the following installed on your computer:
* **Python 3.10 or higher** (Python 3.11, 3.12, or 3.13):
  * Download from [python.org](https://www.python.org/downloads/).
  * *Important on Windows:* Make sure to check the box **"Add python.exe to PATH"** during installation.
* **Git:**
  * Download from [git-scm.com](https://git-scm.com/).
* **FFmpeg** (Required for Manim video animation rendering):
  * **Windows:** Install via PowerShell: `winget install Gyan.FFmpeg` (or download from [ffmpeg.org](https://ffmpeg.org/)).
  * **macOS:** Install via Homebrew: `brew install ffmpeg`.
  * **Linux (Ubuntu/Debian):** `sudo apt update && sudo apt install -y ffmpeg libcairo2-dev libpango1.0-dev`.
* A free **Discord account** and a personal Discord server where you have Administrator rights.

---

## Step 1: Discord Bot Setup (Developer Portal)

The studio uses Discord as your mobile control room. Follow these steps to create your bot:

### 1.1 Create a Discord Application
1. Go to the **[Discord Developer Portal](https://discord.com/developers/applications)** and sign in.
2. Click the blue **"New Application"** button in the top right.
3. Enter a name (e.g., `LinkedIn Studio`) and click **Create**.

### 1.2 Create the Bot & Get Your Bot Token
1. In the left navigation menu, click **"Bot"**.
2. Click **"Reset Token"** (or "View Token") and copy the long token string.
   > ⚠️ **CRITICAL SECURITY NOTE:** Save this token safely. **Never share it publicly or commit it to GitHub.** Anyone with this token can control your bot.

### 1.3 Enable Privileged Message Content Intent (MANDATORY)
1. On the same **"Bot"** page, scroll down to the section titled **"Privileged Gateway Intents"**.
2. Locate **"MESSAGE CONTENT INTENT"** and switch the toggle to **ON** (blue).
3. Click **"Save Changes"** at the bottom.
   > ℹ️ *Why this is needed:* Without this toggle enabled, Discord blocks the bot from reading your text messages (e.g. *"create a carousel for Kafka"*), making it impossible for the bot to respond in chat.

### 1.4 Invite the Bot to Your Discord Server
1. In the left navigation menu, click **"OAuth2"** $\to$ **"URL Generator"**.
2. Under **"Scopes"**, check:
   * `bot`
   * `applications.commands`
3. Under **"Bot Permissions"** (which appears below), check:
   * `Send Messages`
   * `Attach Files`
   * `Read Message History`
   * `Embed Links`
   * `Use External Emojis`
4. Copy the generated URL at the bottom of the page.
5. Paste the URL into your web browser, select your Discord server from the dropdown, and click **Authorize**.
6. You will see your new bot appear offline in your Discord server member list.

---

## Step 2: Google Gemini API Key Setup

The studio's multi-agent think tank (Content Strategist & Staff Engineer Critic) uses Google Gemini to generate high-retention technical hooks and slide decks:

1. Visit **[Google AI Studio](https://aistudio.google.com/)** and sign in with your Google account.
2. Click the **"Get API key"** button.
3. Click **"Create API key in new project"** (or choose an existing project).
4. Copy your API key (it starts with `AIzaSy...`).
   > ℹ️ *Cost note:* Google AI Studio provides generous free-tier usage that easily covers daily content generation.

---

## Step 3: LinkedIn API Setup (Optional)

> 💡 **You can skip this step initially!** If you do not provide a LinkedIn API token, the bot automatically operates in **Safe Simulation Mode**. It will generate and deliver complete ready-to-publish packages (formatted text, videos, and PDF documents) straight to your Discord channel, so you can manually copy and upload them with 1 tap.

If you want the bot to publish autonomously via API:
1. Create a LinkedIn App on the **[LinkedIn Developer Portal](https://www.linkedin.com/developers/)**.
2. Request the **"Share on LinkedIn"** and **"Sign In with LinkedIn"** products.
3. Generate an OAuth 2.0 Access Token with the `w_member_social` permission.
4. Retrieve your LinkedIn Author URN (`urn:li:person:YOUR_ID`).

---

## Step 4: Clone the Code & Install Dependencies

Open your terminal (PowerShell on Windows, or Terminal on macOS/Linux):

### 4.1 Clone Repository
```bash
git clone https://github.com/ahmed-husssain/LinkedInAutomationStudio.git
cd LinkedInAutomationStudio
```

### 4.2 Create & Activate Python Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 4.3 Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 5: Configure Environment Variables (.env)

1. Make a copy of the template file `.env.example` and name it `.env`:
   ```bash
   # Windows (PowerShell)
   Copy-Item .env.example .env

   # macOS / Linux
   cp .env.example .env
   ```

2. Open `.env` in any text editor (VS Code, Notepad, etc.) and fill in your keys:
   ```env
   # Paste your Discord Bot Token from Step 1.2
   DISCORD_BOT_TOKEN=paste_your_discord_bot_token_here

   # Paste your Google Gemini API Key from Step 2
   GEMINI_API_KEY=paste_your_gemini_api_key_here

   # Optional: Leave blank to use Safe Simulation Mode
   LINKEDIN_ACCESS_TOKEN=
   LINKEDIN_AUTHOR_URN=
   ```

3. Save the file.
   > 🔒 *Security reminder:* Your `.env` file is already listed in `.gitignore`. It will never be pushed to GitHub.

---

## Step 6: Run Tests & Launch the Bot

### 6.1 Verify Everything with the Test Suite
Before launching, run the automated test suite to ensure your environment is 100% healthy:
```bash
python -m pytest -v
```
You should see all 39 tests pass with green `PASSED` marks.

### 6.2 Launch the Bot
Start the bot runner:
```bash
python main.py
```

When successful, your console will output:
```text
🚀 Launching LinkedIn Automation Studio Discord Bot...
🤖 LinkedIn Studio Bot is online as LinkedIn Studio#6578 (ID: 1559517565875789828)!
⚡ Background REST Poller active (interval: 1.5s)
⏰ Daily Studio Autopilot loop initialized (24h cadence)
```

Look at your Discord server member list: your bot is now **Online (Green circle)**!

---

## Step 7: How to Use the Studio in Discord

You can now interact with your studio directly from your phone or desktop Discord app:

### 📱 1. Browse Curated Production Topics
Type:
```text
topics
```
The bot will reply with 3 fresh system architecture topics and interactive buttons. Tap any topic button to open the configurator!

### 📄 2. Generate a 6-Slide PDF Carousel Deck
In the topic configurator, tap:
> **`📑 6-Slide PDF Carousel`**

Within seconds, the Carousel Architect will compile a crisp, dark-mode 1080x1350 PDF document and attach it directly in chat. Save it to your phone/computer and upload it as a **"Document"** on LinkedIn for maximum algorithmic reach!

### 🎬 3. Deliver a 60fps Video & Thumbnail
In the topic configurator, tap:
> **`🎬 Short Video (10-15s) + Thumbnail`**

The bot delivers a formatted copy post, an attached playable 1080x1080 MP4 motion graphic, and a standalone custom thumbnail cover.

### 💡 4. Ask for Fresh AI Viral Topics
In chat, type:
```text
suggest some interesting topics for a video or carousel
```
The AI Content Strategist queries Gemini for top 1% real-world Big Tech war stories and returns interactive cards with 1-tap **Video** and **Carousel** generation buttons!

### ✍️ 5. Generate Custom Posts On Demand
Ask the bot to break down any concept you choose:
* *"Create a carousel for Kafka vs RabbitMQ"*
* *"Break down Redis Sentinel failover"*
* *"How does Raft consensus work under network partitions?"*

The Multi-Agent think tank will brainstorm the hook, fact-check the mechanics, format the LinkedIn copy, and compile the full slide deck for you.

---

## 🛠️ Troubleshooting & FAQ

### Q1: The bot is online, but doesn't reply when I send messages.
* **Cause:** The **Privileged Message Content Intent** is disabled in your Discord Developer Portal.
* **Fix:** Go to [discord.com/developers/applications](https://discord.com/developers/applications) $\to$ Select your app $\to$ **Bot** $\to$ Scroll to **Privileged Gateway Intents** $\to$ Turn **ON** `MESSAGE CONTENT INTENT` $\to$ Save Changes $\to$ Restart `python main.py`.

### Q2: Video rendering fails with "ffmpeg not found".
* **Cause:** FFmpeg is not installed or not in your system PATH.
* **Fix:** Install FFmpeg using `winget install Gyan.FFmpeg` (Windows) or `brew install ffmpeg` (macOS), then restart your terminal.

### Q3: How do I run the bot 24/7 in the background on Windows?
You can run the bot as a background process using PowerShell:
```powershell
Start-Process -NoNewWindow python main.py
```
Or deploy it to any cloud VM (AWS EC2, DigitalOcean Droplet, Railway, or Render).

---

🎉 **Congratulations! Your LinkedIn Automation Studio is ready to produce viral engineering content!**
