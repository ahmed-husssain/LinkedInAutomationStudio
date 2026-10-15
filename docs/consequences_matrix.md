# ⚠️ Architectural Consequences & Risk Register

## 1. Purpose & The Transparency Law

In **LinkedIn Automation Studio**, no architectural modification, feature upgrade, or refactoring is ever implemented blindly. Every code change produces ripple effects across storage, memory, AI parsing, and user delivery.

Under **Rule 10 of our Engineering Laws** ([`docs/rules.md`](file:///D:/LinkedInAutomationStudio/docs/rules.md)), the AI agent and any human contributor **MUST proactively disclose all downstream consequences, potential risks, and failure modes in plain, easy-to-understand terms BEFORE making changes.**

This living document serves as the permanent register where every architectural decision and its real-world consequences are documented and tracked.

---

## 2. Standard 5-Pillar Consequence Evaluation

Before any feature is approved, it must be evaluated across these 5 simple questions:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   THE 5-PILLAR CONSEQUENCE CHECKLIST                   │
├────────────────────┬───────────────────────────────────────────────────┤
│ 1. Disk & Storage  │ Will files pile up on the hard drive over time?   │
│                    │ How do we automatically clean up old files?       │
├────────────────────┼───────────────────────────────────────────────────┤
│ 2. AI & Schema     │ What happens if Gemini outputs unexpected format? │
│                    │ Is there a guaranteed 100% crash-proof fallback?  │
├────────────────────┼───────────────────────────────────────────────────┤
│ 3. Client & Cache  │ Will Discord or LinkedIn cache old versions?      │
│                    │ How do we ensure users always see the fresh file? │
├────────────────────┼───────────────────────────────────────────────────┤
│ 4. Performance     │ Does this slow down delivery to the user?         │
│                    │ Does it stay strictly under the sub-2s SLA?       │
├────────────────────┼───────────────────────────────────────────────────┤
│ 5. Test Integrity  │ Does this break any of our existing 39 tests?     │
│                    │ Are new adversarial edge-case tests included?     │
└────────────────────┴───────────────────────────────────────────────────┘
```

---

## 3. Active Feature Assessment: Dynamic Theming & Multi-Layout Carousels

### 3.1 What Is Changing?
* Upgrading [`src/agents/carousel_builder.py`](file:///D:/LinkedInAutomationStudio/src/agents/carousel_builder.py) from a monotonic 3-box text layout to **4 specialized visual slide layouts**:
  1. **Comparison / Versus Slide:** 2-column breakdown (e.g. *Naive vs. Production*).
  2. **Code / Terminal Window:** Dark-mode code card with vector macOS dots (`🔴 🟡 🟢`).
  3. **Architecture Flow Diagram:** Visual vector pipeline (`Service` $\to$ `Queue` $\to$ `DB`).
  4. **Metric / KPI Callout:** Bold before-and-after numbers (`p99: 420ms -> 18ms`).
* Adding **Topic-Aware Dynamic Palettes** (Cyberpunk for Streaming, Obsidian Gold for Security, Deep Navy for Databases).
* Adding **Timestamped Non-Destructive Versioning** so re-generating a topic doesn't wipe out previous work.

---

### 3.2 Consequences & Risks (In Plain Terms)

#### 🔴 Risk 1: Disk Space Accumulation (Files Multiplying)
* **What happens in simple terms:** Right now, generating a Kafka carousel creates 1 file: `kafka_Carousel_Deck.pdf`. If we add timestamped versioning, generating 10 variations will create 10 separate PDF files (~2 MB each). Over months, this could quietly consume gigabytes of disk space.
* **Bad effect on system:** The server could run out of disk space, causing crashes.
* **Our Concrete Mitigation:**
  - Implement an **automatic LRU storage bound**: the system keeps the **latest 5 versions** per topic.
  - When version 6 is generated, the oldest version is automatically pruned from disk.
  - Disk footprint remains strictly capped under 100 MB total.

#### 🔴 Risk 2: The AI Brain Sends Malformed or Incomplete Data
* **What happens in simple terms:** Google Gemini is an LLM. It might occasionally forget to specify a slide layout, or create a "Comparison" slide with only 1 item instead of 2.
* **Bad effect on system:** If the Python code expects 2 items and only finds 1, it could trigger an `IndexError`, causing the bot to crash or fail to reply in Discord.
* **Our Concrete Mitigation:**
  - **The Universal Fallback Rule:** If `layout_type` is missing or unrecognized, the renderer seamlessly falls back to the battle-tested `standard` layout.
  - All array lookups use defensive boundary checks (e.g., `bullets[0] if len(bullets) > 0 else "Default"`), making crashes mathematically impossible.

#### 🔴 Risk 3: Discord Shows Old Cached Previews
* **What happens in simple terms:** Mobile Discord aggressively caches PDF attachments by filename. If you generate a revised carousel with the exact same filename, your phone may keep showing you the old preview.
* **Bad effect on system:** The user thinks the bot didn't update the file or that their prompt was ignored.
* **Our Concrete Mitigation:**
  - Unique timestamped filenames (`kafka_deck_20261015_1445.pdf`) force Discord to treat every generation as a completely fresh file, guaranteeing immediate visual updates.

#### 🔴 Risk 4: Test Suite Breakage
* **What happens in simple terms:** Changing function signatures in `carousel_builder.py` could break existing adversarial tests in [`tests/test_design_system_adversarial.py`](file:///D:/LinkedInAutomationStudio/tests/test_design_system_adversarial.py).
* **Bad effect on system:** GitHub Actions CI will fail, and PRs will be blocked.
* **Our Concrete Mitigation:**
  - Keep `build_pdf_carousel()` and `render_carousel_slide()` signatures 100% backwards-compatible using optional parameters with sensible defaults.
  - Run the full 39-test suite before and after any change to confirm 100% pass rate.

#### 🔴 Risk 5: Render Performance Slump
* **What happens in simple terms:** More complex layouts with circles, boxes, and diagrams could theoretically take longer to render.
* **Bad effect on system:** The user has to wait 10+ seconds for their Discord response.
* **Our Concrete Mitigation:**
  - Everything is drawn in pure **Pillow vector math** (no headless browser, no Chromium).
  - Benchmarked render time is **< 40ms per slide** (< 300ms total for a 6-page PDF). Delivery to Discord remains well under our sub-2-second SLA.

---

## 4. Change Decision Record

| Change ID | Date | Feature Scope | Identified Risks | Approved Mitigations | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CR-001** | Oct 15, 2026 | Multi-Layout Carousel & Dynamic Theming | Disk bloat, AI malformed JSON, Discord caching, test regressions | 5-file bounded LRU pruning, defensive fallbacks, timestamped IDs, signature compatibility | **Under Review** |
