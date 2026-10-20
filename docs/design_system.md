# 🎨 Universal Design System & Spatial Canvas Rules

## 1. Design System Philosophy

The **LinkedIn Automation Studio** visual identity is engineered for **instant mobile comprehension**. 80%+ of LinkedIn technical posts are viewed on mobile devices where readers spend an average of 1.2 to 2.0 seconds evaluating whether to keep scrolling.

To maximize retention and authority, all assets adhere to three foundational pillars:
1. **Dark Mode Engineering Aesthetic:** High-contrast, clean typography, dark backgrounds (Slate, Navy, Obsidian) mimicking developer IDEs and terminal environments.
2. **Zero Collision Safe Zones:** Strict mathematical margins that prevent UI elements, progress scrubbers, or mobile overlays from clipping content.
3. **Deterministic Vector Geometry (Zero Font Tofu):** All badges, arrows, and card structures are drawn programmatically using vector geometry, eliminating missing emoji glyph boxes (`[]`).

> 🌟 **Scenic Presentation Layer:** For detailed specifications on the HTML/Tailwind **"Scenic Dark Luxe"** presentation architecture, topic auroras, and 4-slide storytelling flow, refer to [Scenic UI Presentation Layer Blueprint](SCENIC_UI_PRESENTATION_BLUEPRINT.md).

---

## 2. Canvas Specifications & Aspect Ratios

| Asset Modality | Resolution | Aspect Ratio | Primary Engine | Safe Zone Constraint |
| :--- | :--- | :--- | :--- | :--- |
| **PDF Carousel** | 1080 × 1350 px | **4:5 Vertical** | Pillow (`PIL`) | Top 120px, Bottom 120px, Sides 90px |
| **Motion Graphic Video** | 1080 × 1080 px | **1:1 Square** | Manim CE | $Y \ge -1.8$ (HUD Scrubber Reserved) |
| **Architecture Diagram Card** | 1080 × 1080 px | **1:1 Square** | Pillow (`PIL`) | 80px Border Padding |

---

## 3. PDF Carousel Specification (1080 × 1350 px)

```
+-------------------------------------------------------------+ (0, 0)
| [TOP SAFE ZONE - 120px]                                     |
|  [BADGE: DISTRIBUTED SYSTEMS]               [SLIDE 03 / 06] |
+-------------------------------------------------------------+ (y = 120px)
|                                                             |
|   LEFT MARGIN (90px)                                        |
|   |                                                         |
|   |  TITLE (36pt Bold): The Partition Rebalance Problem     |
|   |  SUBTITLE (22pt): Why consumers stop consuming          |
|   |                                                         |
|   |  +---------------------------------------------------+  |
|   |  | CALLOUT CARD (Background: Dark Card, Border: Cyan)|  |
|   |  | -> Eager Rebalance revokes all partition locks     |  |
|   |  | -> p99 latency spikes during stop-the-world phase  |  |
|   |  +---------------------------------------------------+  |
|   |                                                         |
|   |  KEY TAKEAWAYS (18pt Regular):                          |
|   |  -> Cooperative Sticky assignor migrates partitions     |  |
|   |     incrementally without blocking untouched queues.     |  |
|                                                             |
+-------------------------------------------------------------+ (y = 1230px)
| [BOTTOM SAFE ZONE - 120px]                                  |
|  @engineering-studio                      SWIPE FOR DEEP DIVE >> |
+-------------------------------------------------------------+ (1080, 1350)
```

### 3.1 Margin & Safe Zone Bounds
* **Canvas Dimensions:** $1080 \text{ px (Width)} \times 1350 \text{ px (Height)}$
* **Horizontal Margin:** $X \in [90, 990]$ (90px padding on left and right).
* **Header Safe Zone:** $Y \in [0, 120]$ px. Reserved strictly for topic categories, tags, and slide counters (`01 / 06`).
* **Footer Safe Zone:** $Y \in [1230, 1350]$ px. Reserved strictly for author handles (`@handle`) and mobile swipe prompts (`SWIPE >>`).
* **Active Content Area:** $900 \times 1110$ px ($X \in [90, 990]$, $Y \in [120, 1230]$). No primary text may bleed outside this rectangle.

### 3.2 Typography Scale
* **Cover Hook Headline:** 44–50 pt Bold (Max 3 lines).
* **Slide Heading:** 34–38 pt Bold (Max 2 lines).
* **Section Subtitle:** 22–26 pt Semi-Bold.
* **Body Text & Explanations:** 18–22 pt Regular / Medium.
* **Microcopy & Metadata:** 14–16 pt Medium (Uppercase tracking).

### 3.3 The Zero Font Tofu Rule
> ⚠️ **CRITICAL DIRECTIVE:** Standard TTF/OTF fonts in headless Linux/Windows environments (e.g. DejaVu Sans, Arial) lack colored Unicode emoji glyphs (`👉`, `⚡`, `💬`, `❌`, `✅`). When rendered with PIL, they appear as ugly blank rectangular missing-glyph tofu boxes (`[]`).

**Enforcement:**
* **Never write Unicode emojis directly into slide canvas text.**
* Use **native vector geometry** via PIL `ImageDraw`:
  - Draw bullet points with `draw.ellipse()` or `draw.polygon()` for triangles.
  - Draw arrows using ASCII combinations: `->`, `>>`, `=>`.
  - Draw card borders using `draw.rounded_rectangle()` with `radius=16`.
  - Draw callout accent bars using a solid 4px rectangle on the left border.

---

## 4. Manim Motion Graphics Specification (1080 × 1080 px)

All kinetic video animations in [`src/animations/`](file:///D:/LinkedInAutomationStudio/src/animations/) inherit from `BaseScene` and are rendered at $1080 \times 1080$ resolution at 60fps.

### 4.1 Coordinate Space & HUD Safe Zone
Manim utilizes a centered Cartesian coordinate system where $(0, 0)$ is the center of the viewport:
* $X \in [-4.0, 4.0]$
* $Y \in [-4.0, 4.0]$

```
                +4.0 [TOP BOUNDARY]
                 |
                 |      ACTIVE ANIMATION CANVAS
                 |      (Servers, Queues, Databases, Packets)
                 |      COORDINATE SPACE: Y >= -1.8
                 |
  -4.0 ----------(0, 0)---------- +4.0
                 |
                 |---------------------------------------------
                 |  COLLISION BARRIER LINE (Y = -1.8)
                 |---------------------------------------------
                 |  RESERVED HUD / SCRUBBER SAFE ZONE
                 |  (Progress Bar, Timer, Watermark)
                 |  COORDINATE SPACE: Y in [-3.6, -1.8]
                -4.0 [BOTTOM BOUNDARY]
```

### 4.2 HUD Collision Law
* **The Collision Incident:** Previously, animated elements (such as message queue worker nodes) were centered at $Y = -2.5$, causing the bottom video progress bar and timestamp HUD to collide directly with the text labels.
* **The Invariant:** **ALL animated objects, boxes, arrows, and labels must be placed at $Y \ge -1.8$.**
* Any element attempting to render below $Y = -1.8$ must be shifted upward or scaled down to fit within the upper quadrant.

---

## 5. Color Palette Tokens & Themes

The studio supports 5 calibrated dark-mode palettes:

| Theme Name | Background Color | Surface Card | Primary Text | Muted Text | Primary Accent |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Slate** (Default) | `#0B0F19` | `#1E293B` | `#F8FAFC` | `#94A3B8` | `#38BDF8` (Sky) |
| **Navy** (Enterprise) | `#0A192F` | `#112240` | `#CCD6F6` | `#8892B0` | `#64FFDA` (Teal) |
| **Obsidian** (Mono) | `#121212` | `#1E1E1E` | `#FFFFFF` | `#A0A0A0` | `#E0E0E0` (Silver) |
| **Cyberpunk** (Neon) | `#0D0221` | `#241734` | `#00F0FF` | `#B983FF` | `#FF007F` (Pink) |
| **Emerald** (Fintech) | `#061A14` | `#0D2E24` | `#E6F4EA` | `#82C29B` | `#34D399` (Mint) |

### 5.1 Status & Semantic Accents
* **Success / Verified:** Emerald Green (`#34D399`)
* **Warning / Latency Spike:** Amber Yellow (`#F59E0B`)
* **Failure / Crash / Bottleneck:** Crimson Red (`#EF4444`)
* **Data Flow / In-Flight Request:** Cyan Sky (`#38BDF8`)
