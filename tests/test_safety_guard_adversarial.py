"""
Adversarial Tests for LinkedIn Safety Guard.
Validates atomic state persistence, cooldown enforcement, corrupt files, and clock skew.
"""

import time
import tempfile
from pathlib import Path
import pytest

from src.publishers.safety_guard import LinkedInSafetyGuard


class TestSafetyGuardAdversarial:
    @pytest.fixture
    def temp_state_file(self, tmp_path):
        return tmp_path / "test_publish_state.json"

    def test_missing_state_file_allows_initial_publish(self, temp_state_file):
        """When state file doesn't exist, publishing should be allowed."""
        guard = LinkedInSafetyGuard(state_file=temp_state_file, cooldown_hours=20.0)
        assert guard.can_publish_today() is True
        assert guard.get_remaining_cooldown_hours() == 0.0

    def test_corrupted_zero_byte_state_file_resilience(self, temp_state_file):
        """0-byte corrupted state file should not crash the guard."""
        temp_state_file.write_text("", encoding="utf-8")
        guard = LinkedInSafetyGuard(state_file=temp_state_file, cooldown_hours=20.0)
        assert guard.get_last_published_timestamp() == 0.0
        assert guard.can_publish_today() is True

    def test_malformed_json_state_file_resilience(self, temp_state_file):
        """Corrupt JSON syntax should not crash the guard."""
        temp_state_file.write_text("{malformed: JSON content without closing brace", encoding="utf-8")
        guard = LinkedInSafetyGuard(state_file=temp_state_file, cooldown_hours=20.0)
        assert guard.get_last_published_timestamp() == 0.0
        assert guard.can_publish_today() is True

    def test_non_numeric_and_negative_timestamp(self, temp_state_file):
        """Invalid timestamp values (strings, negative numbers) handled cleanly."""
        temp_state_file.write_text('{"last_published_timestamp": "yesterday"}', encoding="utf-8")
        guard = LinkedInSafetyGuard(state_file=temp_state_file, cooldown_hours=20.0)
        assert guard.get_last_published_timestamp() == 0.0

        temp_state_file.write_text('{"last_published_timestamp": -9999999}', encoding="utf-8")
        assert guard.get_last_published_timestamp() == 0.0

    def test_distant_future_timestamp_clock_skew(self, temp_state_file):
        """Clock skew in future (>24h ahead) is clamped to avoid locking the user forever."""
        future_ts = time.time() + 9999999.0
        temp_state_file.write_text(f'{{"last_published_timestamp": {future_ts}}}', encoding="utf-8")
        guard = LinkedInSafetyGuard(state_file=temp_state_file, cooldown_hours=20.0)
        assert guard.get_last_published_timestamp() == 0.0
        assert guard.can_publish_today() is True

    def test_cooldown_boundary_enforcement(self, temp_state_file):
        """Exact cooldown boundary tests at 19.99h vs 20.01h."""
        guard = LinkedInSafetyGuard(state_file=temp_state_file, cooldown_hours=20.0)
        now = time.time()

        # Published 19.9 hours ago (should be BLOCKED)
        guard.record_successful_post("test_post_1", timestamp=now - (19.9 * 3600))
        assert guard.can_publish_today() is False
        assert guard.get_remaining_cooldown_hours() > 0.0

        # Published 20.1 hours ago (should be ALLOWED)
        guard.record_successful_post("test_post_2", timestamp=now - (20.1 * 3600))
        assert guard.can_publish_today() is True
        assert guard.get_remaining_cooldown_hours() == 0.0

    def test_rapid_consecutive_atomic_writes(self, temp_state_file):
        """Stress-tests atomic write replacing under rapid iterations."""
        guard = LinkedInSafetyGuard(state_file=temp_state_file, cooldown_hours=20.0)
        for i in range(50):
            success = guard.record_successful_post(f"post_{i}")
            assert success is True

        assert temp_state_file.exists()
        assert guard.can_publish_today() is False
