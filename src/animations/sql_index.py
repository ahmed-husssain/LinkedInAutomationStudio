"""
Manim Animation: Why SQL Indexes Make Queries Fast
Duration: ~10-12s
Visualizes:
1. Without Index: Pointer scans through 1,000,000 rows sequentially (Full Table Scan).
2. With B-Tree Index: Root -> Branch -> Leaf in 3 jumps (2ms).
"""

from manim import *

DARK_BG = "#0d1117"
CARD_BG = "#161b22"
CYAN = "#58a6ff"
GREEN = "#3fb950"
RED = "#f85149"
YELLOW = "#e3b341"
MUTED = "#8b949e"

class SqlIndexScene(Scene):
    def construct(self):
        self.camera.background_color = DARK_BG

        # Header
        badge = RoundedRectangle(corner_radius=0.1, height=0.45, width=3.8, color=CYAN, fill_color=CARD_BG, fill_opacity=0.9)
        b_txt = Text("SYSTEM DESIGN IN 10s", font_size=15, color=CYAN, weight=BOLD).move_to(badge.get_center())
        title = Text("Why SQL Indexes Are Fast", font_size=32, weight=BOLD, color=WHITE).next_to(badge, DOWN, buff=0.15)
        self.add(badge, b_txt, title)

        # Left Container: Full Table Scan (No Index)
        box_left = RoundedRectangle(corner_radius=0.15, height=3.2, width=4.5, color=RED, fill_color=CARD_BG, fill_opacity=0.8).move_to(LEFT * 2.8 + DOWN * 0.7)
        lbl_left = Text("NO INDEX (Full Scan)", font_size=18, color=RED, weight=BOLD).next_to(box_left.get_top(), DOWN, buff=0.25)
        
        # Rows
        rows = []
        for i in range(4):
            r = RoundedRectangle(corner_radius=0.08, height=0.35, width=3.8, color="#30363d", fill_color="#21262d", fill_opacity=0.9).move_to(box_left.get_top() + DOWN * (0.8 + i * 0.5))
            rt = Text(f"Row #{i*250000 + 1} ...", font_size=12, color=MUTED).move_to(r.get_center())
            rows.append(VGroup(r, rt))
        
        scan_txt = Text("Checking 1,000,000 rows...", font_size=13, color=RED).move_to(box_left.get_bottom() + UP * 0.3)
        left_grp = VGroup(box_left, lbl_left, *rows, scan_txt)

        # Right Container: B-Tree Index (With Index)
        box_right = RoundedRectangle(corner_radius=0.15, height=3.2, width=4.5, color=GREEN, fill_color=CARD_BG, fill_opacity=0.8).move_to(RIGHT * 2.8 + DOWN * 0.7)
        lbl_right = Text("B-TREE INDEX", font_size=18, color=GREEN, weight=BOLD).next_to(box_right.get_top(), DOWN, buff=0.25)

        # Tree nodes
        root = Circle(radius=0.25, color=CYAN, fill_color=CYAN, fill_opacity=0.8).move_to(box_right.get_top() + DOWN * 0.9)
        rt_lbl = Text("Root", font_size=11, color=BLACK, weight=BOLD).move_to(root.get_center())

        branch = Circle(radius=0.25, color=CYAN, fill_color=CYAN, fill_opacity=0.8).move_to(box_right.get_top() + DOWN * 1.7 + RIGHT * 0.8)
        br_lbl = Text("Branch", font_size=10, color=BLACK, weight=BOLD).move_to(branch.get_center())

        leaf = Circle(radius=0.25, color=GREEN, fill_color=GREEN, fill_opacity=0.8).move_to(box_right.get_top() + DOWN * 2.5 + RIGHT * 1.4)
        lf_lbl = Text("Target", font_size=10, color=BLACK, weight=BOLD).move_to(leaf.get_center())

        line1 = Line(root.get_center(), branch.get_center(), color=CYAN, stroke_width=3)
        line2 = Line(branch.get_center(), leaf.get_center(), color=GREEN, stroke_width=3)

        found_txt = Text("Found in 3 Hops (2ms)!", font_size=14, color=GREEN, weight=BOLD).move_to(box_right.get_bottom() + UP * 0.3)
        right_grp = VGroup(box_right, lbl_right, line1, line2, root, rt_lbl, branch, br_lbl, leaf, lf_lbl, found_txt)

        self.play(Create(box_left), Write(lbl_left), Create(box_right), Write(lbl_right), run_time=1.0)
        self.play(FadeIn(Group(*rows)), FadeIn(scan_txt), run_time=0.8)

        # Scanning pointer animation on left
        pointer = Arrow(LEFT * 5.4, LEFT * 4.8, color=RED, buff=0.1)
        for i in range(4):
            self.play(pointer.animate.move_to(rows[i].get_left() + LEFT * 0.3), run_time=0.3)

        # Instant 3 jumps on right
        self.play(Create(line1), FadeIn(root), FadeIn(rt_lbl), FadeIn(branch), FadeIn(br_lbl), run_time=0.6)
        self.play(Create(line2), FadeIn(leaf), FadeIn(lf_lbl), Write(found_txt), run_time=0.6)

        # Footer takeaway
        bot_bar = RoundedRectangle(corner_radius=0.12, height=0.55, width=9.2, color=YELLOW, fill_color=CARD_BG, fill_opacity=0.98).to_edge(DOWN, buff=0.25)
        bot_txt = Text("TAKEAWAY: O(N) Sequential Disk Reads vs O(log N) Tree Traversal", font_size=16, color=YELLOW, weight=BOLD).move_to(bot_bar.get_center())
        self.play(FadeIn(bot_bar), Write(bot_txt), run_time=0.6)
        self.wait(2.0)


class SqlIndexThumbnail(Scene):
    """1080x1080 Thumbnail for SQL Indexes."""
    def construct(self):
        self.camera.background_color = DARK_BG

        pill = RoundedRectangle(corner_radius=0.15, height=0.6, width=4.8, color=CYAN, fill_color=CARD_BG, fill_opacity=0.95, stroke_width=2).to_edge(UP, buff=0.8)
        pill_txt = Text("SYSTEM DESIGN IN 10s", font_size=20, color=CYAN, weight=BOLD).move_to(pill.get_center())

        title = Text("WHY SQL INDEXES ARE FAST", font_size=50, weight=BOLD, color=WHITE).next_to(pill, DOWN, buff=0.35)
        sub = Text("Full Table Scan vs B-Tree Traversal", font_size=24, color=YELLOW, weight=BOLD).next_to(title, DOWN, buff=0.2)

        left_card = RoundedRectangle(corner_radius=0.2, height=2.2, width=3.4, color=RED, fill_color=CARD_BG, fill_opacity=0.95, stroke_width=3).move_to(LEFT * 3.6 + DOWN * 0.6)
        l_status = Text("WITHOUT INDEX", font_size=22, color=RED, weight=BOLD).move_to(left_card.get_top() + DOWN * 0.5)
        l_desc = Text("Full Table Scan\n1,000,000 rows read", font_size=17, color=WHITE).move_to(left_card.get_bottom() + UP * 0.6)
        left_grp = VGroup(left_card, l_status, l_desc)

        vs = Text("VS", font_size=32, color=YELLOW, weight=BOLD).move_to(DOWN * 0.6)

        right_card = RoundedRectangle(corner_radius=0.2, height=2.2, width=3.4, color=GREEN, fill_color=CARD_BG, fill_opacity=0.95, stroke_width=3).move_to(RIGHT * 3.6 + DOWN * 0.6)
        r_status = Text("WITH B-TREE", font_size=22, color=GREEN, weight=BOLD).move_to(right_card.get_top() + DOWN * 0.5)
        r_desc = Text("Binary Tree Jumps\nFound in 3 Hops (2ms)", font_size=17, color=WHITE).move_to(right_card.get_bottom() + UP * 0.6)
        right_grp = VGroup(right_card, r_status, r_desc)

        footer = RoundedRectangle(corner_radius=0.15, height=0.65, width=9.6, color="#30363d", fill_color=CARD_BG, fill_opacity=0.98).to_edge(DOWN, buff=0.5)
        footer_txt = Text("Used by: PostgreSQL • MySQL InnoDB • SQLite • Oracle", font_size=18, color=MUTED, weight=BOLD).move_to(footer.get_center())

        self.add(pill, pill_txt, title, sub, left_grp, vs, right_grp, footer, footer_txt)
