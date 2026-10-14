"""
LinkedIn Account Safety Guard.
Enforces strict 20-hour cooldown limits using atomic file persistence
to prevent spam flags, account bans, and state corruption.
"""

import os
import json
import time
import tempfile
from pathlib import Path
from typing import Optional, Dict

from src.config.settings import PUBLISH_STATE_FILE, LINKEDIN_COOLDOWN_HOURS


class LinkedInSafetyGuard:
    def __init__(self, state_file: Optional[Path] = None, cooldown_hours: Optional[float] = None):
        self.state_file = state_file or PUBLISH_STATE_FILE
        self.cooldown_hours = cooldown_hours if cooldown_hours is not None else LINKEDIN_COOLDOWN_HOURS

    def get_last_published_timestamp(self) -> float:
        """Reads the last published timestamp safely from the state file."""
        if not self.state_file.exists():
            return 0.0

        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            ts = float(data.get("last_published_timestamp", 0.0))
            # Sanity check against future timestamps (> 1 day in future)
            if ts > time.time() + 86400:
                return 0.0
            return max(0.0, ts)
        except (json.JSONDecodeError, ValueError, OSError):
            return 0.0

    def can_publish_today(self) -> bool:
        """
        Returns True if cooldown period has elapsed since last post.
        Strictly enforces max 1 post per cooldown window.
        """
        last_ts = self.get_last_published_timestamp()
        if last_ts <= 0.0:
            return True

        elapsed_hours = (time.time() - last_ts) / 3600.0
        return elapsed_hours >= self.cooldown_hours

    def get_remaining_cooldown_hours(self) -> float:
        """Returns hours remaining in the cooldown window, or 0.0 if ready."""
        last_ts = self.get_last_published_timestamp()
        if last_ts <= 0.0:
            return 0.0

        elapsed_hours = (time.time() - last_ts) / 3600.0
        remaining = self.cooldown_hours - elapsed_hours
        return max(0.0, round(remaining, 2))

    def record_successful_post(self, post_id: str, timestamp: Optional[float] = None) -> bool:
        """
        Atomically records a successful post timestamp to disk.
        Uses temporary file + atomic rename to prevent 0-byte corruptions.
        """
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        ts = timestamp if timestamp is not None else time.time()

        payload = {
            "last_published_timestamp": ts,
            "last_post_id": str(post_id),
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts)),
        }

        # Atomic write via tempfile in same directory
        temp_dir = self.state_file.parent
        fd, tmp_path = tempfile.mkstemp(dir=temp_dir, prefix="state_", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self.state_file)
            return True
        except Exception:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            return False

    def reset_state(self) -> bool:
        """Clears state file (useful for testing or manual override)."""
        if self.state_file.exists():
            try:
                self.state_file.unlink()
                return True
            except OSError:
                return False
        return True
