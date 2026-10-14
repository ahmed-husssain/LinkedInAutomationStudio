"""
Universal Design System & Spatial Layout Rules.
Governs all Videos (1080x1080), Cover Images (1080x1080), and PDF Carousels (1080x1350).
Strictly prevents visual collisions, text overlapping, and player HUD cutoffs.
"""

from dataclasses import dataclass
from typing import Tuple, List, Optional
import textwrap


# =============================================================================
# 1. COLOR PALETTE (Strict High-Contrast Dark Mode)
# =============================================================================
COLOR_BG_DARK = "#0d1117"        # Pure canvas background
COLOR_CARD_BG = "#161b22"        # Component card background
COLOR_CARD_BORDER = "#30363d"    # Clean structural border
COLOR_TEXT_PRIMARY = "#ffffff"   # Maximum readability
COLOR_TEXT_SECONDARY = "#8b949e" # Secondary explanations & metadata
COLOR_TEXT_MUTED = "#484f58"     # Footers & non-distracting credits

# Accents (Color-blind friendly, high-contrast)
ACCENT_CYAN = "#58a6ff"          # Buffers / Queues / Primary Highlights
ACCENT_GREEN = "#3fb950"         # Workers / DB / Success / Core Superpowers
ACCENT_YELLOW = "#e3b341"        # Producers / API Gateways / Warning
ACCENT_RED = "#f85149"           # Spikes / Outages / Bottlenecks
ACCENT_PURPLE = "#bc8cff"        # Special Protocols / Security


# =============================================================================
# 2. 1080x1080 SQUARE CANVAS (Manim CE Coordinates & PIL Pixels)
# =============================================================================
# Manim 8.0x8.0 Normalized Coordinates:
# X ∈ [-4.0, +4.0], Y ∈ [-4.0, +4.0]

MANIM_ZONE_HEADER_TOP = 3.6
MANIM_ZONE_HEADER_BOTTOM = 2.4

MANIM_ZONE_DIAGRAM_TOP = 2.2
MANIM_ZONE_DIAGRAM_BOTTOM = -0.4

MANIM_ZONE_NARRATIVE_TOP = -0.6
MANIM_ZONE_NARRATIVE_BOTTOM = -1.7

# CRITICAL RULE: Video Player HUD Safe Zone
# Discord, LinkedIn, Instagram scrubber & player controls cover the bottom 15%.
# No text or active card may have y_min < MANIM_BOTTOM_SAFE_LIMIT.
MANIM_BOTTOM_SAFE_LIMIT = -1.8

# Arrow & clearance rules
MANIM_ARROW_BUFFER = 0.20        # Clearance between arrow tip and box edge
MANIM_MIN_ELEMENT_GAP = 0.30     # Minimum distance between any two distinct shapes


# =============================================================================
# 3. 1080x1350 PORTRAIT PDF CAROUSEL PIXEL GRID
# =============================================================================
PDF_WIDTH = 1080
PDF_HEIGHT = 1350

PDF_GUTTER_X = 90                # Left and right page margins
PDF_CONTAINER_TOP = 40
PDF_CONTAINER_BOTTOM = 1310

PDF_ZONE_HEADER_Y = (60, 150)    # Badge and slide counter
PDF_ZONE_TITLE_Y = (180, 340)    # Title & Subtitle zone
PDF_ZONE_CONTENT_Y = (360, 1150) # Cards & Body content zone
PDF_ZONE_FOOTER_Y = (1180, 1290) # Navigation cue & footer credits


# =============================================================================
# 4. TYPOGRAPHY BUDGETS & SMART WORD-WRAPPING
# =============================================================================
def wrap_text_cleanly(text: str, max_chars_per_line: int, max_lines: int = 3) -> List[str]:
    """
    Wraps text strictly at word boundaries.
    Never truncates mid-word or produces overlapping text lines.
    """
    if not text:
        return []
    lines = textwrap.wrap(text.strip(), width=max_chars_per_line)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        if not lines[-1].endswith("..."):
            lines[-1] = lines[-1].rstrip(" .,!?:;") + "..."
    return lines


@dataclass
class BoundingBox2D:
    """Axis-Aligned Bounding Box (AABB) for collision detection."""
    name: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float

    def collides_with(self, other: "BoundingBox2D", padding: float = 0.0) -> bool:
        """Returns True if this bounding box overlaps or violates minimum padding."""
        return not (
            (self.x_max + padding) < other.x_min or
            (self.x_min - padding) > other.x_max or
            (self.y_max + padding) < other.y_min or
            (self.y_min - padding) > other.y_max
        )
