"""
Manim Animation: Cache-Aside Pattern (Redis + Database)
Duration: ~10-12s
Visualizes:
1. Step 1: App checks Redis Cache -> Cache Miss (Key not found).
2. Step 2: App reads PostgreSQL / MySQL Database (Takes 50ms).
3. Step 3: App populates Redis Cache with TTL.
4. Subsequent calls hit Redis in 1ms (Cache Hit!).
"""

from manim import *

DARK_BG = "#0d1117"
CARD_BG = "#161b22"
CYAN = "#58a6ff"
GREEN = "#3fb950"
RED = "#f85149"
YELLOW = "#e3b341"
MUTED = "#8b949e"

class CacheAsideScene(Scene):
    def construct(self):
        self.camera.background_color = DARK_BG

        # 1. Header
        badge = RoundedRectangle(corner_radius=0.1, height=0.45, width=3.8, color=CYAN, fill_color=CARD_BG, fill_opacity=0.9)
        b_txt = Text("SYSTEM DESIGN IN 12s", font_size=15, color=CYAN, weight=BOLD).move_to(badge.get_center())
        title = Text("Cache-Aside Pattern", font_size=32, weight=BOLD, color=WHITE).next_to(badge, DOWN, buff=0.15)
        self.add(badge, b_txt, title)

        # 2. Components: App (Left), Redis Cache (Center), Database (Right)
        app_box = RoundedRectangle(corner_radius=0.15, height=1.6, width=1.8, color=CYAN, fill_color=CARD_BG, fill_opacity=0.9).move_to(LEFT * 4.0 + DOWN * 0.4)
        app_lbl = Text("App Server", font_size=16, color=WHITE, weight=BOLD).move_to(app_box.get_center())

        redis_box = RoundedRectangle(corner_radius=0.15, height=1.6, width=2.0, color=RED, fill_color=CARD_BG, fill_opacity=0.9).move_to(DOWN * 0.4)
        redis_lbl = Text("Redis Cache\n(In-Memory)", font_size=15, color=RED, weight=BOLD).move_to(redis_box.get_center())

        db_box = RoundedRectangle(corner_radius=0.15, height=1.6, width=2.0, color=YELLOW, fill_color=CARD_BG, fill_opacity=0.9).move_to(RIGHT * 4.0 + DOWN * 0.4)
        db_lbl = Text("SQL Database\n(On Disk)", font_size=15, color=YELLOW, weight=BOLD).move_to(db_box.get_center())

        self.play(Create(app_box), Write(app_lbl), Create(redis_box), Write(redis_lbl), Create(db_box), Write(db_lbl), run_time=1.0)

        # Step indicator at bottom
        step_bar = RoundedRectangle(corner_radius=0.12, height=0.55, width=9.2, color="#30363d", fill_color=CARD_BG, fill_opacity=0.95).to_edge(DOWN, buff=0.4)
        step_txt = Text("Step 1: App checks Redis first -> Cache Miss", font_size=17, color=WHITE).move_to(step_bar.get_center())
        self.play(FadeIn(step_bar), Write(step_txt), run_time=0.6)

        # Arrow App -> Redis
        arrow1 = Arrow(app_box.get_right(), redis_box.get_left(), color=CYAN, buff=0.1)
        miss_lbl = Text("Miss (0ms)", font_size=13, color=RED, weight=BOLD).next_to(arrow1, UP, buff=0.1)
        self.play(Create(arrow1), FadeIn(miss_lbl), run_time=0.8)

        # Step 2: Read Database
        step2_txt = Text("Step 2: App fetches row from Database (50ms)", font_size=17, color=YELLOW).move_to(step_bar.get_center())
        self.play(Transform(step_txt, step2_txt), FadeOut(arrow1), FadeOut(miss_lbl), run_time=0.5)

        arrow2 = Arrow(app_box.get_right() + UP * 0.3, db_box.get_left() + UP * 0.3, color=YELLOW, buff=0.1)
        read_lbl = Text("Read DB", font_size=13, color=YELLOW).next_to(arrow2, UP, buff=0.1)
        self.play(Create(arrow2), FadeIn(read_lbl), run_time=0.8)

        # Step 3: Populate Redis
        step3_txt = Text("Step 3: App writes data to Redis with TTL", font_size=17, color=GREEN).move_to(step_bar.get_center())
        self.play(Transform(step_txt, step3_txt), FadeOut(arrow2), FadeOut(read_lbl), run_time=0.5)

        arrow3 = Arrow(app_box.get_right(), redis_box.get_left(), color=GREEN, buff=0.1)
        set_lbl = Text("SET key + TTL", font_size=13, color=GREEN, weight=BOLD).next_to(arrow3, UP, buff=0.1)
        self.play(Create(arrow3), FadeIn(set_lbl), run_time=0.8)

        # Result: Future calls instant Cache Hit (1ms)
        takeaway_bar = RoundedRectangle(corner_radius=0.15, height=0.7, width=9.2, color=GREEN, fill_color=CARD_BG, fill_opacity=0.98).move_to(DOWN * 0.4)
        takeaway_txt = Text("SUBSEQUENT CALLS: Instant Cache Hit (1ms) • DB Protected!", font_size=16, color=GREEN, weight=BOLD).move_to(takeaway_bar.get_center())
        self.play(FadeIn(takeaway_bar), Write(takeaway_txt), FadeOut(arrow3), FadeOut(set_lbl), run_time=0.8)
        self.wait(2.0)
