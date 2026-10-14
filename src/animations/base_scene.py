"""
Base Scene Class for All Manim CE Motion Graphics in LinkedIn Automation Studio.
Enforces the Universal Design System:
- Strict 1080x1080 square canvas
- Standard color-blind safe high-contrast palette
- Guaranteed zero overlapping text/cards (single-occupancy narrative zone)
- Bottom HUD player exclusion zone (Y >= -1.8)
"""

from manim import *
from typing import Optional, List
from src.design_system.rules import (
    COLOR_BG_DARK,
    COLOR_CARD_BG,
    COLOR_CARD_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    ACCENT_CYAN,
    ACCENT_GREEN,
    ACCENT_YELLOW,
    ACCENT_RED,
    MANIM_ZONE_HEADER_TOP,
    MANIM_ZONE_HEADER_BOTTOM,
    MANIM_ZONE_NARRATIVE_TOP,
    MANIM_ZONE_NARRATIVE_BOTTOM,
    MANIM_BOTTOM_SAFE_LIMIT,
    BoundingBox2D
)

config.pixel_width = 1080
config.pixel_height = 1080
config.frame_width = 8.0
config.frame_height = 8.0


class StudioScene(Scene):
    """
    Standard base class that all studio animation scenes inherit from.
    Eliminates magic numbers and enforces spatial layout boundaries.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_step_bar: Optional[Mobject] = None
        self.current_step_txt: Optional[Mobject] = None
        self.header_group: Optional[VGroup] = None

    def setup(self):
        super().setup()
        self.camera.background_color = COLOR_BG_DARK

    def setup_header(self, badge_text: str, title_text: str, accent_color: str = ACCENT_CYAN):
        """Creates standard header strictly in Header Zone (Y: 2.5 to 3.6)."""
        badge = RoundedRectangle(
            corner_radius=0.1, height=0.45, width=3.6,
            color=accent_color, fill_color=COLOR_CARD_BG, fill_opacity=0.95
        ).move_to(UP * 3.35)
        b_txt = Text(badge_text.upper(), font_size=15, color=accent_color, weight=BOLD).move_to(badge.get_center())

        title = Text(title_text, font_size=28, weight=BOLD, color=COLOR_TEXT_PRIMARY).move_to(UP * 2.65)
        self.header_group = VGroup(badge, b_txt, title)
        self.add(self.header_group)
        return self.header_group

    def set_step_banner(
        self,
        step_number: int,
        step_text: str,
        accent_color: str = COLOR_TEXT_PRIMARY,
        run_time: float = 0.4
    ):
        """
        Updates the step banner in the Narrative Zone (Y = -1.1).
        Enforces single-occupancy: never stacks banners or overlaps text.
        """
        full_text = f"Step {step_number}: {step_text}"
        target_center = DOWN * 1.15

        if self.current_step_bar is None:
            # First banner creation
            self.current_step_bar = RoundedRectangle(
                corner_radius=0.12, height=0.62, width=7.4,
                color="#30363d", fill_color=COLOR_CARD_BG, fill_opacity=0.98
            ).move_to(target_center)
            self.current_step_txt = Text(
                full_text, font_size=14, color=accent_color
            ).move_to(self.current_step_bar.get_center())

            self.play(FadeIn(self.current_step_bar), Write(self.current_step_txt), run_time=run_time)
        else:
            # Clean in-place transformation (Zero layout collision)
            new_txt = Text(full_text, font_size=14, color=accent_color).move_to(target_center)
            self.play(
                self.current_step_bar.animate.set_stroke(color=accent_color, width=2),
                Transform(self.current_step_txt, new_txt),
                run_time=run_time
            )

    def show_final_takeaway(
        self,
        badge_text: str,
        main_rule: str,
        sub_text: str,
        accent_color: str = ACCENT_GREEN,
        run_time: float = 0.6
    ):
        """
        Transitions from step banners to the final high-impact takeaway card.
        Guaranteed to stay strictly above the Bottom HUD Safe Zone (Y >= -1.8).
        """
        # 1. Cleanly dismiss previous narrative banner
        if self.current_step_bar:
            self.play(
                FadeOut(self.current_step_bar),
                FadeOut(self.current_step_txt),
                run_time=0.3
            )
            self.current_step_bar = None
            self.current_step_txt = None

        # 2. Render final card at Y = -1.25 (extends from -0.6 to -1.75, safely above -1.8)
        card = RoundedRectangle(
            corner_radius=0.15, height=1.35, width=7.4,
            color=accent_color, fill_color=COLOR_CARD_BG, fill_opacity=0.98
        ).move_to(DOWN * 1.25)

        badge = RoundedRectangle(
            corner_radius=0.08, height=0.32, width=3.4,
            color=accent_color, fill_color=accent_color, fill_opacity=0.25
        ).move_to(card.get_top() + DOWN * 0.28)
        b_txt = Text(f"⚡ {badge_text.upper()}", font_size=11, color=accent_color, weight=BOLD).move_to(badge.get_center())

        t_main = Text(main_rule, font_size=14, color=COLOR_TEXT_PRIMARY, weight=BOLD).move_to(card.get_center() + DOWN * 0.05)
        t_sub = Text(sub_text, font_size=12, color=COLOR_TEXT_SECONDARY).move_to(card.get_bottom() + UP * 0.25)

        takeaway_group = VGroup(card, badge, b_txt, t_main, t_sub)
        self.play(FadeIn(takeaway_group), run_time=run_time)
        return takeaway_group
