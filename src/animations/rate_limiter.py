"""
Enhanced 20-Second Manim Animation: Token Bucket Rate Limiter
Explains with high visual clarity:
1. Exact Algorithm: Token Bucket (AWS / Stripe standard)
2. Capacity & Refill rate HUD
3. The Superpower: Burst traffic handling (3 reqs at once -> 200 OK)
4. Rate limit breach: Empty bucket -> HTTP 429 Throttled
5. Auto-recovery: Next tick refills -> Req succeeds
Total duration: ~19-20 seconds.
"""

from manim import *

DARK_BG = "#0d1117"
CARD_BG = "#161b22"
CYAN = "#58a6ff"
GREEN = "#3fb950"
RED = "#f85149"
YELLOW = "#e3b341"
MUTED = "#8b949e"

class TokenBucketScene(Scene):
    def construct(self):
        self.camera.background_color = DARK_BG

        # -------------------------------------------------------------
        # 1. HEADER & HUD (0.0s - 2.5s)
        # -------------------------------------------------------------
        badge = RoundedRectangle(corner_radius=0.1, height=0.45, width=3.4, color=CYAN, fill_color=CARD_BG, fill_opacity=0.9)
        badge_txt = Text("SYSTEM DESIGN BREAKDOWN", font_size=15, color=CYAN, weight=BOLD).move_to(badge.get_center())
        header_grp = VGroup(badge, badge_txt).to_edge(UP, buff=0.4)

        title = Text("Token Bucket Rate Limiter", font_size=32, weight=BOLD, color=WHITE).next_to(header_grp, DOWN, buff=0.2)
        
        # HUD Panel (Top Right): Current Token Counter
        hud_box = RoundedRectangle(corner_radius=0.15, height=0.7, width=3.0, color=MUTED, fill_color=CARD_BG, fill_opacity=0.9).to_corner(UR, buff=0.5)
        hud_label = Text("TOKENS: 3 / 3", font_size=18, color=YELLOW, weight=BOLD).move_to(hud_box.get_center())
        hud_grp = VGroup(hud_box, hud_label)

        # Step Indicator Banner (Bottom)
        step_bg = RoundedRectangle(corner_radius=0.15, height=0.6, width=9.0, color="#30363d", fill_color=CARD_BG, fill_opacity=0.95).to_edge(DOWN, buff=0.5)
        step_txt = Text("Step 1: Background timer refills +1 token/sec (Cap = 3)", font_size=19, color=WHITE).move_to(step_bg.get_center())

        self.play(FadeIn(header_grp), Write(title), FadeIn(hud_grp), FadeIn(step_bg), Write(step_txt), run_time=1.4)

        # -------------------------------------------------------------
        # 2. THE BUCKET & REFILL SPOUT (2.5s - 5.5s)
        # -------------------------------------------------------------
        # Bucket Container (Center-Right)
        bucket_w, bucket_h = 2.0, 2.4
        b_left = Line(LEFT * (bucket_w/2) + DOWN * 1.5, LEFT * (bucket_w/2) + UP * 0.9, color=CYAN, stroke_width=4)
        b_bottom = Line(LEFT * (bucket_w/2) + DOWN * 1.5, RIGHT * (bucket_w/2) + DOWN * 1.5, color=CYAN, stroke_width=4)
        b_right = Line(RIGHT * (bucket_w/2) + DOWN * 1.5, RIGHT * (bucket_w/2) + UP * 0.9, color=CYAN, stroke_width=4)
        bucket = VGroup(b_left, b_bottom, b_right).move_to(RIGHT * 0.2 + DOWN * 0.3)

        b_title = Text("Token Bucket", font_size=18, color=CYAN, weight=BOLD).next_to(bucket, DOWN, buff=0.2)
        b_sub = Text("Max Capacity = 3", font_size=14, color=MUTED).next_to(b_title, DOWN, buff=0.1)

        # Target Server (Far Right)
        server_box = RoundedRectangle(corner_radius=0.15, height=2.0, width=1.8, color="#8b949e", fill_color=CARD_BG, fill_opacity=0.9).move_to(RIGHT * 4.0 + DOWN * 0.3)
        server_title = Text("API\nServer", font_size=18, color=WHITE, weight=BOLD).move_to(server_box.get_center())
        server_grp = VGroup(server_box, server_title)

        self.play(Create(bucket), Write(b_title), FadeIn(b_sub), Create(server_grp), run_time=1.2)

        # Refill 3 tokens into the bucket
        token_positions = [
            bucket.get_bottom() + UP * 0.45,
            bucket.get_bottom() + UP * 1.15,
            bucket.get_bottom() + UP * 1.85,
        ]
        tokens = []
        for i, pos in enumerate(token_positions):
            tok = Circle(radius=0.28, color=CYAN, fill_color=CYAN, fill_opacity=0.85, stroke_width=2)
            lbl = Text(f"T{i+1}", font_size=15, color=BLACK, weight=BOLD).move_to(tok.get_center())
            t_grp = VGroup(tok, lbl).move_to(bucket.get_top() + UP * 1.0)
            self.play(t_grp.animate.move_to(pos), run_time=0.4)
            tokens.append(t_grp)

        self.wait(0.4)

        # -------------------------------------------------------------
        # 3. BURST TRAFFIC HANDLING (5.5s - 10.5s)
        # -------------------------------------------------------------
        # Update step banner
        step2_txt = Text("Step 2: BURST TRAFFIC (3 calls at once) -> All tokens claimed!", font_size=19, color=GREEN).move_to(step_bg.get_center())
        self.play(Transform(step_txt, step2_txt), run_time=0.5)

        # 3 incoming requests arriving together (burst)
        req_colors = [GREEN, GREEN, GREEN]
        req_labels = ["Req #1", "Req #2", "Req #3"]
        burst_reqs = []

        for i in range(3):
            r_box = RoundedRectangle(corner_radius=0.12, height=0.5, width=1.3, color=GREEN, fill_color=GREEN, fill_opacity=0.25)
            r_txt = Text(req_labels[i], font_size=15, color=GREEN, weight=BOLD).move_to(r_box.get_center())
            r_grp = VGroup(r_box, r_txt).move_to(LEFT * 4.2 + UP * (0.8 - i * 0.75))
            burst_reqs.append(r_grp)

        self.play(FadeIn(Group(*burst_reqs)), run_time=0.6)

        # Each request claims 1 token and passes into the Server as 200 OK
        for i in range(3):
            tok = tokens.pop()
            req = burst_reqs[i]
            
            # Request moves to bucket, takes token, turns to 200 OK
            ok_txt = Text("200 OK", font_size=15, color=GREEN, weight=BOLD).move_to(req.get_center())
            self.play(
                req.animate.move_to(bucket.get_left() + LEFT * 0.4),
                tok.animate.move_to(bucket.get_left() + LEFT * 0.4).scale(0.5),
                run_time=0.45
            )
            self.play(
                FadeOut(tok),
                Transform(req[1], ok_txt),
                req.animate.move_to(server_box.get_center() + UP * (0.5 - i * 0.5)).scale(0.8),
                run_time=0.5
            )
            # Update HUD
            new_hud = Text(f"TOKENS: {2 - i} / 3", font_size=18, color=RED if (2-i)==0 else YELLOW, weight=BOLD).move_to(hud_box.get_center())
            self.play(Transform(hud_label, new_hud), run_time=0.15)

        self.wait(0.5)

        # -------------------------------------------------------------
        # 4. RATE LIMIT BREACH -> HTTP 429 (10.5s - 15.0s)
        # -------------------------------------------------------------
        step3_txt = Text("Step 3: Bucket is EMPTY (0/3). Next request arrives -> THROTTLED!", font_size=19, color=RED).move_to(step_bg.get_center())
        self.play(Transform(step_txt, step3_txt), run_time=0.5)

        # Req #4 arrives
        req4_box = RoundedRectangle(corner_radius=0.12, height=0.55, width=1.4, color=RED, fill_color=RED, fill_opacity=0.3)
        req4_txt = Text("Req #4", font_size=16, color=RED, weight=BOLD).move_to(req4_box.get_center())
        req4 = VGroup(req4_box, req4_txt).move_to(LEFT * 4.2 + DOWN * 0.3)

        self.play(FadeIn(req4), run_time=0.4)
        self.play(req4.animate.move_to(bucket.get_left() + LEFT * 0.8), run_time=0.6)

        # Blocked: No token available! Red shield / 429 status
        barrier = Line(UP * 0.8, DOWN * 1.5, color=RED, stroke_width=6).move_to(bucket.get_left() + LEFT * 0.2)
        err_badge = RoundedRectangle(corner_radius=0.1, height=0.5, width=3.2, color=RED, fill_color=CARD_BG, fill_opacity=0.95).move_to(UP * 1.7 + LEFT * 1.0)
        err_txt = Text("HTTP 429 Too Many Requests", font_size=15, color=RED, weight=BOLD).move_to(err_badge.get_center())
        err_grp = VGroup(err_badge, err_txt)

        self.play(Create(barrier), FadeIn(err_grp), req4.animate.shift(LEFT * 0.4), run_time=0.7)
        self.wait(0.8)

        # -------------------------------------------------------------
        # 5. AUTO-RECOVERY VIA REFILL (15.0s - 19.5s)
        # -------------------------------------------------------------
        step4_txt = Text("Step 4: Clock ticks 1 sec -> +1 Token refills -> Service recovers!", font_size=19, color=CYAN).move_to(step_bg.get_center())
        self.play(
            FadeOut(barrier),
            FadeOut(err_grp),
            FadeOut(req4),
            Transform(step_txt, step4_txt),
            run_time=0.6
        )

        # A new token drops in
        new_token = Circle(radius=0.28, color=CYAN, fill_color=CYAN, fill_opacity=0.85, stroke_width=2)
        new_t_lbl = Text("T1", font_size=15, color=BLACK, weight=BOLD).move_to(new_token.get_center())
        new_t_grp = VGroup(new_token, new_t_lbl).move_to(bucket.get_top() + UP * 1.0)

        recovered_hud = Text("TOKENS: 1 / 3", font_size=18, color=GREEN, weight=BOLD).move_to(hud_box.get_center())
        self.play(
            new_t_grp.animate.move_to(token_positions[0]),
            Transform(hud_label, recovered_hud),
            run_time=0.7
        )

        # Summary takeaway pill
        takeaway_box = RoundedRectangle(corner_radius=0.15, height=0.75, width=9.2, color=YELLOW, fill_color=CARD_BG, fill_opacity=0.98).move_to(DOWN * 0.3)
        takeaway_txt = Text("KEY TAKEAWAY: Token Bucket allows bursts, then caps at refill rate.", font_size=18, color=YELLOW, weight=BOLD).move_to(takeaway_box.get_center())
        takeaway_grp = VGroup(takeaway_box, takeaway_txt)

        self.play(FadeIn(takeaway_grp), run_time=0.7)
        self.wait(2.0)


class TokenBucketThumbnail(Scene):
    """
    Renders a dedicated, high-contrast 1080x1080 thumbnail image.
    Designed for maximum Click-Through Rate (CTR) in LinkedIn's feed.
    """
    def construct(self):
        self.camera.background_color = DARK_BG

        # 1. Top Category Pill
        pill_box = RoundedRectangle(corner_radius=0.15, height=0.6, width=4.8, color=CYAN, fill_color=CARD_BG, fill_opacity=0.95, stroke_width=2)
        pill_txt = Text("SYSTEM DESIGN IN 20s", font_size=20, color=CYAN, weight=BOLD).move_to(pill_box.get_center())
        pill = VGroup(pill_box, pill_txt).to_edge(UP, buff=0.8)

        # 2. Giant High-Impact Title
        title = Text("TOKEN BUCKET", font_size=58, weight=BOLD, color=WHITE).next_to(pill, DOWN, buff=0.35)
        sub = Text("How Rate Limiters Handle Bursts & 429s", font_size=24, color=YELLOW, weight=BOLD).next_to(title, DOWN, buff=0.2)

        # 3. Central Bucket Graphic
        b_w, b_h = 2.4, 2.6
        b_left = Line(LEFT * (b_w/2) + DOWN * 1.6, LEFT * (b_w/2) + UP * 1.0, color=CYAN, stroke_width=6)
        b_bottom = Line(LEFT * (b_w/2) + DOWN * 1.6, RIGHT * (b_w/2) + DOWN * 1.6, color=CYAN, stroke_width=6)
        b_right = Line(RIGHT * (b_w/2) + DOWN * 1.6, RIGHT * (b_w/2) + UP * 1.0, color=CYAN, stroke_width=6)
        bucket = VGroup(b_left, b_bottom, b_right).move_to(DOWN * 0.4)

        b_label = Text("Bucket (Cap = 3)", font_size=20, color=CYAN, weight=BOLD).next_to(bucket, DOWN, buff=0.3)

        # 3 Glowing Tokens Inside
        tok1 = Circle(radius=0.35, color=CYAN, fill_color=CYAN, fill_opacity=0.9, stroke_width=2).move_to(bucket.get_bottom() + UP * 0.55)
        t1_lbl = Text("T1", font_size=20, color=BLACK, weight=BOLD).move_to(tok1.get_center())
        tok2 = Circle(radius=0.35, color=CYAN, fill_color=CYAN, fill_opacity=0.9, stroke_width=2).move_to(bucket.get_bottom() + UP * 1.35)
        t2_lbl = Text("T2", font_size=20, color=BLACK, weight=BOLD).move_to(tok2.get_center())
        tok3 = Circle(radius=0.35, color=CYAN, fill_color=CYAN, fill_opacity=0.9, stroke_width=2).move_to(bucket.get_bottom() + UP * 2.15)
        t3_lbl = Text("T3", font_size=20, color=BLACK, weight=BOLD).move_to(tok3.get_center())
        tokens_grp = VGroup(tok1, t1_lbl, tok2, t2_lbl, tok3, t3_lbl)

        # 4. Left Feature Card: "Burst Allowed (200 OK)"
        left_card = RoundedRectangle(corner_radius=0.2, height=1.6, width=2.8, color=GREEN, fill_color=CARD_BG, fill_opacity=0.95, stroke_width=3).move_to(LEFT * 3.8 + DOWN * 0.4)
        l_status = Text("200 OK", font_size=26, color=GREEN, weight=BOLD).move_to(left_card.get_top() + DOWN * 0.45)
        l_desc = Text("Burst Traffic\nAllowed", font_size=16, color=WHITE).move_to(left_card.get_bottom() + UP * 0.45)
        left_grp = VGroup(left_card, l_status, l_desc)

        # 5. Right Feature Card: "Throttled (429 Error)"
        right_card = RoundedRectangle(corner_radius=0.2, height=1.6, width=2.8, color=RED, fill_color=CARD_BG, fill_opacity=0.95, stroke_width=3).move_to(RIGHT * 3.8 + DOWN * 0.4)
        r_status = Text("429 ERROR", font_size=26, color=RED, weight=BOLD).move_to(right_card.get_top() + DOWN * 0.45)
        r_desc = Text("When Empty:\nThrottled!", font_size=16, color=WHITE).move_to(right_card.get_bottom() + UP * 0.45)
        right_grp = VGroup(right_card, r_status, r_desc)

        # 6. Bottom Banner
        bot_banner = RoundedRectangle(corner_radius=0.15, height=0.65, width=9.6, color="#30363d", fill_color=CARD_BG, fill_opacity=0.98).to_edge(DOWN, buff=0.5)
        bot_txt = Text("Used by: AWS API Gateway • Stripe • Cloudflare", font_size=18, color=MUTED, weight=BOLD).move_to(bot_banner.get_center())
        bot_grp = VGroup(bot_banner, bot_txt)

        self.add(pill, title, sub, bucket, b_label, tokens_grp, left_grp, right_grp, bot_grp)

