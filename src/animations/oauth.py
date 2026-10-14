"""
Manim 2D Motion Visual: How OAuth 2.0 Works (Clearly Explained in Under 15s)
Inspired by top tech motion visualizers (Nikki Siapno style):
- Dark mode (#0d1117)
- 4 Actors: User / Browser, Client App, Auth Server (Google), Resource Server (API)
- Smooth animated tokens & payload transfers
- 4 Clear Steps:
  1. User -> Auth Server: "Log in with Google" (Consent)
  2. Auth Server -> Client: Temporary Auth Code (code=xyz)
  3. Client -> Auth Server: Exchange Code for Access Token
  4. Client -> Resource Server: Fetch Profile with Bearer Token!
- Final Rule: "The Client NEVER sees your password!"
"""

from manim import *

# Configure native square frame (1080x1080)
config.pixel_width = 1080
config.pixel_height = 1080
config.frame_width = 8.0
config.frame_height = 8.0

DARK_BG = "#0d1117"
CARD_BG = "#161b22"
CYAN = "#58a6ff"
GREEN = "#3fb950"
YELLOW = "#e3b341"
PURPLE = "#bc8cff"
RED = "#f85149"
MUTED = "#8b949e"

class OAuthScene(Scene):
    def construct(self):
        self.camera.background_color = DARK_BG

        # 1. Header Badge & Title (Centered at top)
        badge = RoundedRectangle(corner_radius=0.1, height=0.45, width=3.6, color=CYAN, fill_color=CARD_BG, fill_opacity=0.95).move_to(UP * 3.35)
        b_txt = Text("SYSTEM DESIGN IN 15s", font_size=15, color=CYAN, weight=BOLD).move_to(badge.get_center())
        title = Text("How OAuth 2.0 Works", font_size=32, weight=BOLD, color=WHITE).move_to(UP * 2.65)
        self.add(badge, b_txt, title)

        # 2. Actors Layout (4 Nodes in 2x2 Grid filling square canvas)
        # Top-Left: User / Browser
        user_box = RoundedRectangle(corner_radius=0.15, height=1.45, width=2.8, color=CYAN, fill_color=CARD_BG, fill_opacity=0.95).move_to(LEFT * 2.2 + UP * 1.1)
        user_lbl = Text("1. User\n(Browser)", font_size=15, color=CYAN, weight=BOLD).move_to(user_box.get_center())

        # Top-Right: Auth Server (Google / IDP)
        auth_box = RoundedRectangle(corner_radius=0.15, height=1.45, width=2.8, color=GREEN, fill_color=CARD_BG, fill_opacity=0.95).move_to(RIGHT * 2.2 + UP * 1.1)
        auth_lbl = Text("2. Auth Server\n(Google IDP)", font_size=15, color=GREEN, weight=BOLD).move_to(auth_box.get_center())

        # Bottom-Left: Client App (Your Website)
        app_box = RoundedRectangle(corner_radius=0.15, height=1.45, width=2.8, color=YELLOW, fill_color=CARD_BG, fill_opacity=0.95).move_to(LEFT * 2.2 + DOWN * 0.9)
        app_lbl = Text("3. Client App\n(Backend Server)", font_size=15, color=YELLOW, weight=BOLD).move_to(app_box.get_center())

        # Bottom-Right: Resource Server (API / Profile)
        api_box = RoundedRectangle(corner_radius=0.15, height=1.45, width=2.8, color=PURPLE, fill_color=CARD_BG, fill_opacity=0.95).move_to(RIGHT * 2.2 + DOWN * 0.9)
        api_lbl = Text("4. Resource API\n(User Data)", font_size=15, color=PURPLE, weight=BOLD).move_to(api_box.get_center())

        self.play(Create(user_box), Write(user_lbl),
                  Create(auth_box), Write(auth_lbl),
                  Create(app_box), Write(app_lbl),
                  Create(api_box), Write(api_lbl), run_time=0.9)

        # Step Banner at Bottom
        step_bar = RoundedRectangle(corner_radius=0.12, height=0.58, width=7.4, color="#30363d", fill_color=CARD_BG, fill_opacity=0.95).move_to(DOWN * 3.35)
        step_txt = Text("Step 1: User logs into Google & approves consent", font_size=15, color=WHITE).move_to(step_bar.get_center())
        self.play(FadeIn(step_bar), Write(step_txt), run_time=0.5)

        # -------------------------------------------------------------
        # STEP 1: User grants consent to Auth Server (Top horizontal)
        # -------------------------------------------------------------
        arrow1 = Arrow(user_box.get_right(), auth_box.get_left(), color=CYAN, buff=0.12)
        p1 = RoundedRectangle(corner_radius=0.08, height=0.38, width=1.6, color=CYAN, fill_color=CYAN, fill_opacity=0.3)
        p1_txt = Text("Consent OK", font_size=12, color=CYAN, weight=BOLD).move_to(p1.get_center())
        p1_grp = VGroup(p1, p1_txt).move_to(user_box.get_right() + RIGHT * 0.2)

        self.play(Create(arrow1), FadeIn(p1_grp), p1_grp.animate.move_to(auth_box.get_left() + LEFT * 0.2), run_time=0.8)
        self.play(FadeOut(p1_grp), FadeOut(arrow1), run_time=0.2)

        # -------------------------------------------------------------
        # STEP 2: Auth Server returns temporary Auth Code to Client
        # -------------------------------------------------------------
        step2_txt = Text("Step 2: Google redirects with temporary Auth Code", font_size=15, color=YELLOW).move_to(step_bar.get_center())
        self.play(Transform(step_txt, step2_txt), run_time=0.4)

        arrow2 = Arrow(auth_box.get_bottom() + LEFT * 0.4, app_box.get_top() + RIGHT * 0.4, color=YELLOW, buff=0.12)
        code_badge = RoundedRectangle(corner_radius=0.08, height=0.38, width=1.6, color=YELLOW, fill_color=YELLOW, fill_opacity=0.3)
        code_txt = Text("code=xyz", font_size=12, color=YELLOW, weight=BOLD).move_to(code_badge.get_center())
        code_grp = VGroup(code_badge, code_txt).move_to(auth_box.get_bottom() + LEFT * 0.4)

        self.play(Create(arrow2), FadeIn(code_grp), code_grp.animate.move_to(app_box.get_top() + RIGHT * 0.4), run_time=0.8)
        self.play(FadeOut(code_grp), FadeOut(arrow2), run_time=0.2)

        # -------------------------------------------------------------
        # STEP 3: Client exchanges Auth Code for Access Token
        # -------------------------------------------------------------
        step3_txt = Text("Step 3: Backend exchanges Code for Access Token (JWT)", font_size=15, color=GREEN).move_to(step_bar.get_center())
        self.play(Transform(step_txt, step3_txt), run_time=0.4)

        token_req = Arrow(app_box.get_top() + RIGHT * 0.6, auth_box.get_bottom() + LEFT * 0.2, color=GREEN, buff=0.12)
        token_badge = RoundedRectangle(corner_radius=0.08, height=0.38, width=2.0, color=GREEN, fill_color=GREEN, fill_opacity=0.3)
        token_txt = Text("Access Token", font_size=12, color=GREEN, weight=BOLD).move_to(token_badge.get_center())
        token_grp = VGroup(token_badge, token_txt).move_to(app_box.get_top() + RIGHT * 0.6)

        self.play(Create(token_req), FadeIn(token_grp), token_grp.animate.move_to(auth_box.get_bottom() + LEFT * 0.2), run_time=0.8)
        self.play(FadeOut(token_grp), FadeOut(token_req), run_time=0.2)

        # -------------------------------------------------------------
        # STEP 4: Client fetches Profile from Resource API
        # -------------------------------------------------------------
        step4_txt = Text("Step 4: Client presents Bearer Token -> 200 Profile", font_size=15, color=PURPLE).move_to(step_bar.get_center())
        self.play(Transform(step_txt, step4_txt), run_time=0.4)

        arrow4 = Arrow(app_box.get_right(), api_box.get_left(), color=PURPLE, buff=0.12)
        api_res = RoundedRectangle(corner_radius=0.08, height=0.38, width=2.0, color=PURPLE, fill_color=PURPLE, fill_opacity=0.3)
        api_txt = Text("200 User Profile", font_size=12, color=PURPLE, weight=BOLD).move_to(api_res.get_center())
        api_grp = VGroup(api_res, api_txt).move_to(app_box.get_right() + RIGHT * 0.2)

        self.play(Create(arrow4), FadeIn(api_grp), api_grp.animate.move_to(api_box.get_left() + LEFT * 0.2), run_time=0.8)
        self.play(FadeOut(api_grp), FadeOut(arrow4), run_time=0.2)

        # -------------------------------------------------------------
        # FINAL CORE TAKEAWAY
        # -------------------------------------------------------------
        takeaway_bar = RoundedRectangle(corner_radius=0.12, height=0.68, width=7.4, color=GREEN, fill_color=CARD_BG, fill_opacity=0.98).move_to(DOWN * 2.25)
        takeaway_txt = Text("CORE RULE: Third-party app NEVER sees user's password!", font_size=14, color=GREEN, weight=BOLD).move_to(takeaway_bar.get_center())
        self.play(FadeIn(takeaway_bar), FadeIn(takeaway_txt), run_time=0.7)
        self.wait(2.2)


class OAuthThumbnail(Scene):
    """1080x1080 custom thumbnail cover for OAuth 2.0."""
    def construct(self):
        self.camera.background_color = DARK_BG

        badge = RoundedRectangle(corner_radius=0.12, height=0.52, width=3.8, color=CYAN, fill_color=CARD_BG, fill_opacity=0.95).move_to(UP * 3.3)
        b_txt = Text("SYSTEM DESIGN IN 15s", font_size=16, color=CYAN, weight=BOLD).move_to(badge.get_center())
        title = Text("HOW OAUTH 2.0 WORKS", font_size=36, weight=BOLD, color=WHITE).move_to(UP * 2.5)
        sub = Text("Why third-party apps never see your Google password", font_size=18, color=MUTED).move_to(UP * 1.85)
        self.add(badge, b_txt, title, sub)

        # 3 Step Visual Cards (spanning [-3.6, +3.6])
        c1 = RoundedRectangle(corner_radius=0.15, height=3.2, width=2.3, color=CYAN, fill_color=CARD_BG, fill_opacity=0.95).move_to(LEFT * 2.5 + DOWN * 0.4)
        c1_t = Text("1. Consent", font_size=17, color=CYAN, weight=BOLD).move_to(c1.get_top() + DOWN * 0.45)
        c1_b = Text("User approves\npermissions\non Google login", font_size=15, color=WHITE).move_to(c1.get_center() + DOWN * 0.25)

        c2 = RoundedRectangle(corner_radius=0.15, height=3.2, width=2.3, color=YELLOW, fill_color=CARD_BG, fill_opacity=0.95).move_to(DOWN * 0.4)
        c2_t = Text("2. Auth Code", font_size=17, color=YELLOW, weight=BOLD).move_to(c2.get_top() + DOWN * 0.45)
        c2_b = Text("Temporary code\nexchanged on\nbackend server", font_size=15, color=WHITE).move_to(c2.get_center() + DOWN * 0.25)

        c3 = RoundedRectangle(corner_radius=0.15, height=3.2, width=2.3, color=GREEN, fill_color=CARD_BG, fill_opacity=0.95).move_to(RIGHT * 2.5 + DOWN * 0.4)
        c3_t = Text("3. Access Token", font_size=17, color=GREEN, weight=BOLD).move_to(c3.get_top() + DOWN * 0.45)
        c3_b = Text("Scoped Bearer\ntoken fetches\nuser profile", font_size=15, color=WHITE).move_to(c3.get_center() + DOWN * 0.25)

        self.add(c1, c1_t, c1_b, c2, c2_t, c2_b, c3, c3_t, c3_b)

        footer = Text("Short Visual Breakdown • Swipe for Architecture Details", font_size=16, color=MUTED).move_to(DOWN * 3.35)
        self.add(footer)
