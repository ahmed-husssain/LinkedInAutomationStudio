"""
Manim 2D Motion Graphic: Why Message Queues Save Crashing APIs
Built on StudioScene Base Class (Universal Design System):
- 1080x1080 square canvas, 60fps
- Zero text collisions / no overlapping divs
- Safe margin strictly above Y = -1.8 for mobile player controls
"""

from manim import *
from src.animations.base_scene import StudioScene
from src.design_system.rules import (
    COLOR_CARD_BG,
    ACCENT_CYAN,
    ACCENT_GREEN,
    ACCENT_YELLOW,
    ACCENT_RED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED
)


class QueueScene(StudioScene):
    def construct(self):
        # 1. Standard Design System Header
        self.setup_header("SYSTEM DESIGN IN 15s", "Why Message Queues Save APIs", ACCENT_CYAN)

        # 2. Components in Diagram Arena (Y = 0.75, strictly within [-0.4, 2.2])
        api_box = RoundedRectangle(
            corner_radius=0.15, height=1.6, width=2.2,
            color=ACCENT_YELLOW, fill_color=COLOR_CARD_BG, fill_opacity=0.95
        ).move_to(LEFT * 2.6 + UP * 0.75)
        api_lbl = Text("API Gateway\n(Producers)", font_size=14, color=ACCENT_YELLOW, weight=BOLD).move_to(api_box.get_center())

        queue_box = RoundedRectangle(
            corner_radius=0.15, height=1.6, width=2.2,
            color=ACCENT_CYAN, fill_color=COLOR_CARD_BG, fill_opacity=0.95
        ).move_to(UP * 0.75)
        queue_lbl = Text("Message Queue\n(Buffer / RAM)", font_size=14, color=ACCENT_CYAN, weight=BOLD).move_to(queue_box.get_center())

        db_box = RoundedRectangle(
            corner_radius=0.15, height=1.6, width=2.2,
            color=ACCENT_GREEN, fill_color=COLOR_CARD_BG, fill_opacity=0.95
        ).move_to(RIGHT * 2.6 + UP * 0.75)
        db_lbl = Text("Worker + DB\n(Consumers)", font_size=14, color=ACCENT_GREEN, weight=BOLD).move_to(db_box.get_center())

        self.play(
            Create(api_box), Write(api_lbl),
            Create(queue_box), Write(queue_lbl),
            Create(db_box), Write(db_lbl),
            run_time=0.8
        )

        # -------------------------------------------------------------
        # STEP 1: Traffic Surge (Single-Occupancy Narrative Banner)
        # -------------------------------------------------------------
        self.set_step_banner(1, "Sudden traffic surge (10,000 req/s) hits API", ACCENT_YELLOW)

        arrow1 = Arrow(api_box.get_right(), queue_box.get_left(), color=ACCENT_YELLOW, buff=0.15)
        p1 = RoundedRectangle(corner_radius=0.08, height=0.36, width=1.4, color=ACCENT_RED, fill_color=ACCENT_RED, fill_opacity=0.3)
        p1_txt = Text("10k req/s", font_size=11, color=ACCENT_RED, weight=BOLD).move_to(p1.get_center())
        p1_grp = VGroup(p1, p1_txt).move_to(api_box.get_right() + RIGHT * 0.1)

        self.play(Create(arrow1), FadeIn(p1_grp), p1_grp.animate.move_to(queue_box.get_left() + LEFT * 0.1), run_time=0.8)
        self.play(FadeOut(p1_grp), FadeOut(arrow1), run_time=0.2)

        # -------------------------------------------------------------
        # STEP 2: Queue Buffers Safely
        # -------------------------------------------------------------
        self.set_step_banner(2, "Queue buffers all bursts safely in RAM/Disk", ACCENT_CYAN)

        q_item1 = RoundedRectangle(corner_radius=0.05, height=0.25, width=1.8, color=ACCENT_CYAN, fill_color=ACCENT_CYAN, fill_opacity=0.4).move_to(queue_box.get_center() + DOWN * 0.4)
        q_item2 = RoundedRectangle(corner_radius=0.05, height=0.25, width=1.8, color=ACCENT_CYAN, fill_color=ACCENT_CYAN, fill_opacity=0.4).move_to(queue_box.get_center() + DOWN * 0.1)
        q_items = VGroup(q_item1, q_item2)
        self.play(FadeIn(q_items), queue_box.animate.set_stroke(color=ACCENT_CYAN, width=4), run_time=0.7)

        # -------------------------------------------------------------
        # STEP 3: Workers process at safe, steady pace (500 req/s)
        # -------------------------------------------------------------
        self.set_step_banner(3, "Workers pull at steady 500 req/s (Database Safe!)", ACCENT_GREEN)

        arrow2 = Arrow(queue_box.get_right(), db_box.get_left(), color=ACCENT_GREEN, buff=0.15)
        w_flow = RoundedRectangle(corner_radius=0.08, height=0.36, width=1.4, color=ACCENT_GREEN, fill_color=ACCENT_GREEN, fill_opacity=0.3)
        w_txt = Text("Steady 500/s", font_size=11, color=ACCENT_GREEN, weight=BOLD).move_to(w_flow.get_center())
        w_grp = VGroup(w_flow, w_txt).move_to(queue_box.get_right() + RIGHT * 0.1)

        self.play(Create(arrow2), FadeIn(w_grp), w_grp.animate.move_to(db_box.get_left() + LEFT * 0.1), run_time=0.8)
        self.play(FadeOut(w_grp), FadeOut(arrow2), FadeOut(q_items), run_time=0.3)

        # -------------------------------------------------------------
        # FINAL CORE TAKEAWAY (Safe Transition, Zero Overlap)
        # -------------------------------------------------------------
        self.show_final_takeaway(
            badge_text="CORE SUPERPOWER",
            main_rule="Queues absorb shocks so databases never drown!",
            sub_text="Transforms violent traffic bursts into predictable, steady throughput.",
            accent_color=ACCENT_GREEN
        )
        self.wait(2.2)


class QueueThumbnail(StudioScene):
    """1080x1080 custom thumbnail cover for Message Queues."""
    def construct(self):
        badge = RoundedRectangle(corner_radius=0.12, height=0.52, width=3.8, color=ACCENT_CYAN, fill_color=COLOR_CARD_BG, fill_opacity=0.95).move_to(UP * 3.3)
        b_txt = Text("SYSTEM DESIGN IN 15s", font_size=16, color=ACCENT_CYAN, weight=BOLD).move_to(badge.get_center())
        title1 = Text("WHY MESSAGE QUEUES", font_size=28, weight=BOLD, color=COLOR_TEXT_PRIMARY).move_to(UP * 2.6)
        title2 = Text("SAVE CRASHING APIS", font_size=28, weight=BOLD, color=ACCENT_CYAN).move_to(UP * 2.1)
        sub = Text("Surviving 10,000 req/s traffic spikes without crashing", font_size=16, color=COLOR_TEXT_MUTED).move_to(UP * 1.55)
        self.add(badge, b_txt, title1, title2, sub)

        # 3 Step Visual Cards
        c1 = RoundedRectangle(corner_radius=0.15, height=2.8, width=2.3, color=ACCENT_RED, fill_color=COLOR_CARD_BG, fill_opacity=0.95).move_to(LEFT * 2.5 + DOWN * 0.35)
        c1_t = Text("1. The Surge", font_size=16, color=ACCENT_RED, weight=BOLD).move_to(c1.get_top() + DOWN * 0.45)
        c1_b = Text("10,000 req/s\nsudden spike\nhits backend", font_size=14, color=COLOR_TEXT_PRIMARY).move_to(c1.get_center() + DOWN * 0.25)

        c2 = RoundedRectangle(corner_radius=0.15, height=2.8, width=2.3, color=ACCENT_CYAN, fill_color=COLOR_CARD_BG, fill_opacity=0.95).move_to(DOWN * 0.35)
        c2_t = Text("2. The Buffer", font_size=16, color=ACCENT_CYAN, weight=BOLD).move_to(c2.get_top() + DOWN * 0.45)
        c2_b = Text("RabbitMQ / SQS\nsafely absorbs\nburst in RAM", font_size=14, color=COLOR_TEXT_PRIMARY).move_to(c2.get_center() + DOWN * 0.25)

        c3 = RoundedRectangle(corner_radius=0.15, height=2.8, width=2.3, color=ACCENT_GREEN, fill_color=COLOR_CARD_BG, fill_opacity=0.95).move_to(RIGHT * 2.5 + DOWN * 0.35)
        c3_t = Text("3. The Stream", font_size=16, color=ACCENT_GREEN, weight=BOLD).move_to(c3.get_top() + DOWN * 0.45)
        c3_b = Text("Workers process\nat steady 500/s\nZero data loss", font_size=14, color=COLOR_TEXT_PRIMARY).move_to(c3.get_center() + DOWN * 0.25)

        self.add(c1, c1_t, c1_b, c2, c2_t, c2_b, c3, c3_t, c3_b)

        footer = Text("Short Visual Breakdown • Swipe for Architecture Details", font_size=15, color=COLOR_TEXT_MUTED).move_to(DOWN * 2.45)
        self.add(footer)
