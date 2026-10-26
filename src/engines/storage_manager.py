"""
Storage Manager & Janitor for LinkedIn Automation Studio.
Enforces two-tier storage (drafts/ vs published/), 24h TTL auto-pruning,
and hard disk quota enforcement using only Python standard library.
"""

import os
import time
import shutil
import logging
from pathlib import Path
from typing import Optional, List

from src.config.settings import ASSETS_DIR

logger = logging.getLogger("StorageManager")

DRAFTS_DIR = ASSETS_DIR / "drafts"
PUBLISHED_DIR = ASSETS_DIR / "published"
DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)


def purge_draft(file_path: Path | str) -> bool:
    """Instantly deletes a draft file from disk if it exists."""
    p = Path(file_path)
    try:
        if p.exists() and p.is_file():
            p.unlink()
            logger.info("Purged draft: %s", p.name)
            return True
    except OSError as e:
        logger.warning("Failed to purge %s: %s", p.name, e)
    return False


def promote_to_published(draft_path: Path | str, target_name: Optional[str] = None) -> Path:
    """Moves an approved draft to published storage atomically."""
    src = Path(draft_path)
    if not src.exists() or not src.is_file():
        raise FileNotFoundError(f"Draft file not found: {src}")

    dst_name = Path(target_name or src.name).name
    dst = (PUBLISHED_DIR / dst_name).resolve()
    if not dst.is_relative_to(PUBLISHED_DIR.resolve()):
        raise ValueError(f"Security: Target path '{dst}' escapes PUBLISHED_DIR '{PUBLISHED_DIR}'")
    shutil.move(str(src), str(dst))
    logger.info("Promoted %s -> %s", src.name, dst.name)
    return dst


def prune_expired_drafts(max_age_hours: float = 24.0, directory: Optional[Path] = None) -> int:
    """Deletes unapproved drafts older than max_age_hours."""
    target_dir = directory or DRAFTS_DIR
    if not target_dir.exists():
        return 0

    cutoff = time.time() - (max_age_hours * 3600)
    pruned = 0
    for item in target_dir.iterdir():
        if item.is_file() and item.stat().st_mtime < cutoff:
            if purge_draft(item):
                pruned += 1
    return pruned


def enforce_disk_quota(
    max_mb: float = 200.0,
    target_mb: float = 100.0,
    directory: Optional[Path] = None
) -> int:
    """Enforces disk ceiling; purges oldest files if total size exceeds max_mb."""
    target_dir = directory or DRAFTS_DIR
    if not target_dir.exists():
        return 0

    max_bytes = max_mb * 1024 * 1024
    target_bytes = target_mb * 1024 * 1024

    files: List[Path] = [f for f in target_dir.iterdir() if f.is_file()]
    total_size = sum(f.stat().st_size for f in files)

    if total_size <= max_bytes:
        return 0

    # Sort oldest first (LRU eviction)
    files.sort(key=lambda f: f.stat().st_mtime)
    pruned = 0
    for f in files:
        size = f.stat().st_size
        if purge_draft(f):
            total_size -= size
            pruned += 1
        if total_size <= target_bytes:
            break
    return pruned
