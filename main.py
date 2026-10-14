"""
LinkedIn Automation Studio - Main Entrypoint
"""

import sys
from pathlib import Path

# Fix Windows console UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from src.bot.client import run_bot

if __name__ == "__main__":
    run_bot()
