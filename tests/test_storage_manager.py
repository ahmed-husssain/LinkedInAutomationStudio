"""
Unit and Adversarial Tests for Storage Manager & Janitor.
Verifies instant draft purging, published promotion, 24h TTL pruning, and disk quota enforcement.
"""

import os
import time
from pathlib import Path
import pytest

from src.engines.storage_manager import (
    purge_draft,
    promote_to_published,
    prune_expired_drafts,
    enforce_disk_quota,
    DRAFTS_DIR,
    PUBLISHED_DIR,
)


def test_purge_draft(tmp_path: Path):
    test_file = tmp_path / "test_draft.pdf"
    test_file.write_bytes(b"dummy pdf bytes")
    assert test_file.exists()

    # Successful purge
    assert purge_draft(test_file) is True
    assert not test_file.exists()

    # Non-existent purge does not throw and returns False
    assert purge_draft(test_file) is False


def test_promote_to_published(tmp_path: Path, monkeypatch):
    test_published_dir = tmp_path / "published"
    test_published_dir.mkdir()
    monkeypatch.setattr("src.engines.storage_manager.PUBLISHED_DIR", test_published_dir)

    draft = tmp_path / "draft.pdf"
    draft.write_text("content")

    promoted = promote_to_published(draft, "final.pdf")
    assert promoted.exists()
    assert promoted.name == "final.pdf"
    assert not draft.exists()

    # Promoting nonexistent file raises FileNotFoundError
    with pytest.raises(FileNotFoundError):
        promote_to_published(tmp_path / "missing.pdf")


def test_prune_expired_drafts(tmp_path: Path):
    # Old file (30 hours old)
    old_file = tmp_path / "old.pdf"
    old_file.write_bytes(b"old")
    past_time = time.time() - (30 * 3600)
    os.utime(old_file, (past_time, past_time))

    # Fresh file (1 hour old)
    fresh_file = tmp_path / "fresh.pdf"
    fresh_file.write_bytes(b"fresh")

    pruned = prune_expired_drafts(max_age_hours=24.0, directory=tmp_path)
    assert pruned == 1
    assert not old_file.exists()
    assert fresh_file.exists()


def test_enforce_disk_quota(tmp_path: Path):
    # Create 3 files of 1 MB each (total 3 MB)
    file1 = tmp_path / "f1.bin"
    file2 = tmp_path / "f2.bin"
    file3 = tmp_path / "f3.bin"

    now = time.time()
    for i, f in enumerate([file1, file2, file3]):
        f.write_bytes(b"x" * (1024 * 1024))
        # f1 oldest, f2 middle, f3 newest
        t = now - (100 - i * 10)
        os.utime(f, (t, t))

    # Total is 3MB. Set max to 2MB, target to 1MB.
    # Should prune f1 and f2 to get under or equal to 1MB.
    pruned = enforce_disk_quota(max_mb=2.0, target_mb=1.0, directory=tmp_path)
    # Total size was 3MB > 2MB -> Pruned oldest (f1 and f2) until size <= 1MB
    assert pruned == 2
    assert not file1.exists()
    assert not file2.exists()
    assert file3.exists()


def test_enforce_disk_quota_under_limit(tmp_path: Path):
    file1 = tmp_path / "tiny.bin"
    file1.write_bytes(b"small")

    pruned = enforce_disk_quota(max_mb=100.0, target_mb=50.0, directory=tmp_path)
    assert pruned == 0
    assert file1.exists()
