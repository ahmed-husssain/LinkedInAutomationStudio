"""
Manim Animation: API Idempotency (Why Double Clicks Won't Charge You Twice)
Duration: ~12-14 seconds (Snappy, punchy).
Visualizes:
1. Click #1 with Idempotency-Key: uuid-1 -> Charged $50, cached in Redis.
2. Click #2 (Accidental Double Click / Retry) with SAME Key -> Cached response returned, NO double charge!
"""

from manim import *

DARK_BG = "#0d1117"
CARD_BG = "#161b22"
CYAN = "#58a6ff"
GREEN = "#3fb950"
YELLOW = "#e3b341"
RED = "#f85149"
MUTED = "#8b949e"

class IdempotencyScene(Scene):
    def construct(self):
        self.camera.background_color = DARK_BG

        # 1. Header
        badge = RoundedRectangle(corner_radius=0.1, height=0.45, width=3.8, color=CYAN, fill_color=CARD_BG, fill_opacity=0.9)
        b_txt = Text("SYSTEM DESIGN IN 12s", font_size=15, color=CYAN, weight=BOLD).move_to(badge.get_center())
        title = Text("API Idempotency", font_size=32, weight=BOLD, color=WHITE).next_to(badge, DOWN, buff=0.15)
        self.add(badge, b_txt, title)

        # 2. Components: Client (Left), API Server (Center), Redis (Right)
        client = RoundedRectangle(corner_radius=0.15, height=1.6, width=1.8, color="#58a6ff", fill_color=CARD_BG, fill_opacity=0.9).move_to(LEFT * 4.2 + DOWN * 0.5)
        c_lbl = Text("Mobile\nClient", font_size=16, color=WHITE, weight=BOLD).move_to(client.get_center())

        server = RoundedRectangle(corner_radius=0.15, height=1.6, width=1.8, color="#8b949e", fill_color=CARD_BG, fill_opacity=0.9).move_to(DOWN * 0.5)
        s_lbl = Text("Payment\nServer", font_size=16, color=WHITE, weight=BOLD).move_to(server.get_center())

        redis_box = RoundedRectangle(corner_radius=0.15, height=1.6, width=2.0, color=RED, fill_color=CARD_BG, fill_opacity=0.9).move_to(RIGHT * 4.0 + DOWN * 0.5)
        r_lbl = Text("Redis Cache\n(Key Store)", font_size=15, color=RED, weight=BOLD).move_to(redis_box.get_center())

        self.play(Create(client), Write(c_lbl), Create(server), Write(s_lbl), Create(redis_box), Write(r_lbl), run_time=1.0)

        # Step indicator at bottom
        step_bar = RoundedRectangle(corner_radius=0.12, height=0.55, width=9.2, color="#30363d", fill_color=CARD_BG, fill_opacity=0.95).to_edge(DOWN, buff=0.4)
        step_txt = Text("Step 1: First Click sends unique Idempotency-Key: uuid-1", font_size=18, color=WHITE).move_to(step_bar.get_center())
        self.play(FadeIn(step_bar), Write(step_txt), run_time=0.6)

        # 3. Request 1: POST /pay (with Key: uuid-1)
        req1 = RoundedRectangle(corner_radius=0.1, height=0.5, width=1.5, color=GREEN, fill_color=GREEN, fill_opacity=0.3)
        req1_txt = Text("POST: uuid-1", font_size=13, color=GREEN, weight=BOLD).move_to(req1.get_center())
        req1_grp = VGroup(req1, req1_txt).move_to(client.get_right() + RIGHT * 0.2)

        self.play(FadeIn(req1_grp), req1_grp.animate.move_to(server.get_left() + LEFT * 0.2), run_time=0.8)

        # Server checks Redis -> Miss -> Saves to Redis
        save_line = Arrow(server.get_right(), redis_box.get_left(), color=YELLOW, buff=0.1)
        key_saved = Text("Set: uuid-1 -> Paid", font_size=13, color=YELLOW).next_to(save_line, UP, buff=0.1)
        self.play(Create(save_line), FadeIn(key_saved), run_time=0.7)

        # Returns 200 OK ($50 Charged)
        res1 = RoundedRectangle(corner_radius=0.1, height=0.5, width=1.5, color=GREEN, fill_color=GREEN, fill_opacity=0.3)
        res1_txt = Text("200 Charged", font_size=13, color=GREEN, weight=BOLD).move_to(res1.get_center())
        res1_grp = VGroup(res1, res1_txt).move_to(server.get_left() + LEFT * 0.2)

        self.play(FadeOut(req1_grp), FadeIn(res1_grp), res1_grp.animate.move_to(client.get_right() + RIGHT * 0.2), run_time=0.8)
        self.play(FadeOut(res1_grp), run_time=0.3)

        # -------------------------------------------------------------
        # 4. Request 2: ACCIDENTAL DOUBLE CLICK!
        # -------------------------------------------------------------
        step2_txt = Text("Step 2: Accidental Double-Click sends SAME key: uuid-1", font_size=18, color=YELLOW).move_to(step_bar.get_center())
        self.play(Transform(step_txt, step2_txt), FadeOut(save_line), FadeOut(key_saved), run_time=0.5)

        req2 = RoundedRectangle(corner_radius=0.1, height=0.5, width=1.5, color=YELLOW, fill_color=YELLOW, fill_opacity=0.3)
        req2_txt = Text("Retry: uuid-1", font_size=13, color=YELLOW, weight=BOLD).move_to(req2.get_center())
        req2_grp = VGroup(req2, req2_txt).move_to(client.get_right() + RIGHT * 0.2)

        self.play(FadeIn(req2_grp), req2_grp.animate.move_to(server.get_left() + LEFT * 0.2), run_time=0.8)

        # Server checks Redis -> CACHE HIT!
        hit_badge = RoundedRectangle(corner_radius=0.1, height=0.45, width=2.4, color=CYAN, fill_color=CARD_BG, fill_opacity=0.95).move_to(UP * 1.5)
        hit_txt = Text("CACHE HIT in Redis!", font_size=15, color=CYAN, weight=BOLD).move_to(hit_badge.get_center())
        self.play(FadeIn(hit_badge), FadeIn(hit_txt), run_time=0.6)

        # Server returns cached response (NO SECOND CHARGE!)
        safe_res = RoundedRectangle(corner_radius=0.1, height=0.5, width=1.6, color=CYAN, fill_color=CYAN, fill_opacity=0.3)
        safe_txt = Text("200 (Cached)", font_size=13, color=CYAN, weight=BOLD).move_to(safe_res.get_center())
        safe_grp = VGroup(safe_res, safe_txt).move_to(server.get_left() + LEFT * 0.2)

        self.play(FadeOut(req2_grp), FadeIn(safe_grp), safe_grp.animate.move_to(client.get_right() + RIGHT * 0.2), run_time=0.8)

        # 5. Takeaway
        takeaway_bar = RoundedRectangle(corner_radius=0.15, height=0.7, width=9.2, color=GREEN, fill_color=CARD_BG, fill_opacity=0.98).move_to(DOWN * 0.5)
        takeaway_txt = Text("PROTECTED: 1 Card Charge • 2 Instant Responses • 0 Duplicates", font_size=17, color=GREEN, weight=BOLD).move_to(takeaway_bar.get_center())
        self.play(FadeIn(takeaway_bar), Write(takeaway_txt), run_time=0.8)
        self.wait(2.0)


class IdempotencyThumbnail(Scene):
    """1080x1080 high-contrast thumbnail for API Idempotency."""
    def construct(self):
        self.camera.background_color = DARK_BG

        pill = RoundedRectangle(corner_radius=0.15, height=0.6, width=4.8, color=CYAN, fill_color=CARD_BG, fill_opacity=0.95, stroke_width=2).to_edge(UP, buff=0.8)
        pill_txt = Text("SYSTEM DESIGN IN 12s", font_size=20, color=CYAN, weight=BOLD).move_to(pill.get_center())

        title = Text("API IDEMPOTENCY", font_size=56, weight=BOLD, color=WHITE).next_to(pill, DOWN, buff=0.35)
        sub = Text("Why Double Clicks Won't Charge You Twice", font_size=24, color=YELLOW, weight=BOLD).next_to(title, DOWN, buff=0.2)

        # Left Card (Click 1)
        left_card = RoundedRectangle(corner_radius=0.2, height=2.2, width=3.2, color=GREEN, fill_color=CARD_BG, fill_opacity=0.95, stroke_width=3).move_to(LEFT * 3.6 + DOWN * 0.6)
        l_status = Text("1st Click", font_size=24, color=GREEN, weight=BOLD).move_to(left_card.get_top() + DOWN * 0.5)
        l_desc = Text("200 OK\nCharged $50", font_size=18, color=WHITE).move_to(left_card.get_bottom() + UP * 0.6)
        left_grp = VGroup(left_card, l_status, l_desc)

        # Center Redis Icon
        redis_box = RoundedRectangle(corner_radius=0.2, height=1.8, width=2.4, color=RED, fill_color=CARD_BG, fill_opacity=0.95, stroke_width=3).move_to(DOWN * 0.6)
        r_title = Text("Redis Cache", font_size=20, color=RED, weight=BOLD).move_to(redis_box.get_top() + DOWN * 0.45)
        r_key = Text("uuid-1 : PAID", font_size=15, color=YELLOW).move_to(redis_box.get_bottom() + UP * 0.45)
        redis_grp = VGroup(redis_box, r_title, r_key)

        # Right Card (Click 2)
        right_card = RoundedRectangle(corner_radius=0.2, height=2.2, width=3.2, color=CYAN, fill_color=CARD_BG, fill_opacity=0.95, stroke_width=3).move_to(RIGHT * 3.6 + DOWN * 0.6)
        r_status = Text("2nd Click", font_size=24, color=CYAN, weight=BOLD).move_to(right_card.get_top() + DOWN * 0.5)
        r_desc = Text("200 Cached\nNO Double Charge!", font_size=17, color=WHITE).move_to(right_card.get_bottom() + UP * 0.6)
        right_grp = VGroup(right_card, r_status, r_desc)

        # Footer
        footer = RoundedRectangle(corner_radius=0.15, height=0.65, width=9.6, color="#30363d", fill_color=CARD_BG, fill_opacity=0.98).to_edge(DOWN, buff=0.5)
        footer_txt = Text("Used by: Stripe • PayPal • Shopify Payment Gateways", font_size=18, color=MUTED, weight=BOLD).move_to(footer.get_center())

        self.add(pill, pill_txt, title, sub, left_grp, redis_grp, right_grp, footer, footer_txt)
