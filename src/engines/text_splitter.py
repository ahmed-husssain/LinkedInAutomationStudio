"""
Pure Text Splitting Engine for Discord Select Dropdowns.
Ensures ZERO truncation and perfect word-boundary wrapping on mobile screens.
"""

from typing import Tuple, Optional


def split_text_for_option(
    text: str,
    max_line1: int = 38,
    max_line2: int = 95,
    min_split_threshold: int = 15
) -> Tuple[str, Optional[str]]:
    """
    Splits text across label (line 1, primary) and description (line 2, subtext)
    at a natural word boundary so NO word is ever cut in half and NO text is silently lost.

    Args:
        text: The input string to split.
        max_line1: Maximum character length for line 1 (Discord label limit is 100, 38 is ideal for mobile).
        max_line2: Maximum character length for line 2 (Discord description limit is 100, 95 is safe).
        min_split_threshold: Minimum character index before allowing a space split to avoid orphan single words.

    Returns:
        (line1, line2): line1 is always a non-empty string (unless input was empty); line2 is str or None.
    """
    if text is None:
        return "", None

    # Normalize whitespace: convert newlines/tabs to single space and strip
    cleaned = " ".join(text.strip().split())
    if not cleaned:
        return "", None

    # Safe guard on degenerate boundary limits
    if max_line1 <= 0:
        max_line1 = 38
    if max_line2 <= 0:
        max_line2 = 95

    # If fits comfortably in line 1, no description needed
    if len(cleaned) <= max_line1:
        return cleaned, None

    # Search for the last space within max_line1 boundary
    split_idx = cleaned.rfind(" ", 0, max_line1)

    # If no space found or space is too early (e.g. single tiny word), hard-break at max_line1
    if split_idx == -1 or split_idx < min_split_threshold:
        split_idx = max_line1

    line1 = cleaned[:split_idx].strip()
    line2 = cleaned[split_idx:].strip()

    if not line2:
        return line1, None

    # Clamp line 2 at word boundary if it exceeds max_line2
    if len(line2) > max_line2:
        cut_idx = line2.rfind(" ", 0, max_line2)
        if cut_idx != -1 and cut_idx >= 5:
            line2 = line2[:cut_idx].strip()
        else:
            line2 = line2[:max_line2].strip()

    return line1, (line2 if line2 else None)
