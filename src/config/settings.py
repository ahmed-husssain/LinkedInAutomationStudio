"""
Configuration & Environment Settings for LinkedIn Automation Studio.
"""

import os
import sys
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = BASE_DIR / "src"
ASSETS_DIR = BASE_DIR / "assets"
VIDEOS_DIR = ASSETS_DIR / "videos"
THUMBNAILS_DIR = ASSETS_DIR / "thumbnails"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Try loading .env if available
try:
    from dotenv import load_dotenv
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

# Discord Settings
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "").strip()
DISCORD_POLL_INTERVAL_SECONDS = float(os.getenv("DISCORD_POLL_INTERVAL", "1.5"))
MESSAGE_CACHE_MAX_SIZE = int(os.getenv("MESSAGE_CACHE_MAX_SIZE", "1000"))

# LinkedIn Settings
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "").strip()
LINKEDIN_AUTHOR_URN = os.getenv("LINKEDIN_AUTHOR_URN", "").strip()
LINKEDIN_COOLDOWN_HOURS = float(os.getenv("LINKEDIN_COOLDOWN_HOURS", "20.0"))
PUBLISH_STATE_FILE = DATA_DIR / "publish_state.json"

# Google Gemini API Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
GEMINI_FAST_MODEL = os.getenv("GEMINI_FAST_MODEL", "gemini-flash-latest")

# Quality & Output Specs
CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1080
DEFAULT_ACCENT_COLOR = "#58a6ff"
