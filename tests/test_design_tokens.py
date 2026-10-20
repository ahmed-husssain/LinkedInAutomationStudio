"""
Unit Tests for Apple-Grade Design Foundation Tokens.
Verifies size-specific optical tracking, topology aspect ratio resolution,
and native CSS custom property generation.
"""

from src.design_system.tokens import (
    TYPOGRAPHY_TOKENS,
    CANVAS_ASPECT_RATIOS,
    LUMINANCE_RAMPS,
    resolve_topology_aspect_ratio,
    generate_css_tokens,
)


def test_typography_optical_tracking_hierarchy():
    """Verifies that large display headings have negative tracking and small badges have positive tracking."""
    # 1. Large display headline must be tightly kerned (-0.03em)
    display = TYPOGRAPHY_TOKENS["display"]
    assert float(display["letter_spacing"].replace("em", "")) < 0
    assert display["letter_spacing"] == "-0.03em"
    assert display["text_wrap"] == "balance"

    # 2. Uppercase badge must have open positive tracking (+0.08em) for legibility
    badge = TYPOGRAPHY_TOKENS["badge"]
    assert float(badge["letter_spacing"].replace("em", "")) > 0
    assert badge["letter_spacing"] == "0.08em"
    assert badge["text_transform"] == "uppercase"

    # 3. Monospace token must enforce tabular-nums for vertical metric alignment
    mono = TYPOGRAPHY_TOKENS["mono"]
    assert mono["font_variant_numeric"] == "tabular-nums"


def test_topology_aspect_ratio_resolution():
    """Verifies content-driven aspect ratio assignment based on concept topology."""
    # 1. Horizontal stream / event pipelines -> landscape (16:9)
    assert resolve_topology_aspect_ratio(["kafka", "streaming"], "Partition Rebalance") == "landscape"
    assert resolve_topology_aspect_ratio(["microservices"], "Distributed Saga Pipeline") == "landscape"

    # 2. Cyclic feedback loops / rate limiters -> square (1:1)
    assert resolve_topology_aspect_ratio(["networking"], "Token Bucket Rate Limiter") == "square"
    assert resolve_topology_aspect_ratio(["resilience"], "Circuit Breaker State Machine") == "square"

    # 3. Narrative causality step-by-step -> portrait (4:5)
    assert resolve_topology_aspect_ratio(["incident"], "Why PostgreSQL Locks Exploded at 3 AM") == "portrait"


def test_canvas_geometries_integrity():
    """Verifies aspect ratios match standard high-fidelity resolutions."""
    assert CANVAS_ASPECT_RATIOS["landscape"]["ratio"] == "16:9"
    assert CANVAS_ASPECT_RATIOS["landscape"]["width"] == 1920
    assert CANVAS_ASPECT_RATIOS["landscape"]["height"] == 1080

    assert CANVAS_ASPECT_RATIOS["portrait"]["ratio"] == "4:5"
    assert CANVAS_ASPECT_RATIOS["portrait"]["width"] == 1080
    assert CANVAS_ASPECT_RATIOS["portrait"]["height"] == 1350

    assert CANVAS_ASPECT_RATIOS["square"]["ratio"] == "1:1"
    assert CANVAS_ASPECT_RATIOS["square"]["width"] == 1080
    assert CANVAS_ASPECT_RATIOS["square"]["height"] == 1080


def test_glass_material_specular_bevel():
    """Verifies Apple-grade specular glass material properties."""
    glass = LUMINANCE_RAMPS["glass"]
    assert "bevel_top" in glass
    assert "0.18" in glass["bevel_top"]  # Physical top-edge reflection
    assert glass["radius"] == "20px"     # Squircle curvature


def test_generate_css_tokens():
    """Verifies CSS tokens generator produces valid native CSS without build steps."""
    css = generate_css_tokens()
    assert ":root" in css
    assert "--font-display-ls: -0.03em;" in css
    assert "--glass-bevel-top" in css
    assert ".scenic-glass" in css
    assert ".scenic-tabular" in css
    assert "font-variant-numeric: tabular-nums;" in css
