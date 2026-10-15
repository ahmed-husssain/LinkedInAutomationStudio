# 🗺️ Scope & Product Roadmap

This document outlines the strategic scope, phased milestones, and long-term vision of **LinkedIn Automation Studio**. It defines what is being built, what the final system looks like, and what boundaries are strictly out-of-scope.

---

## 🌟 The North Star Vision

The ultimate vision is an **Autonomous End-to-End Distributed Systems Media Factory**: a self-sustaining engine that detects breaking production outages and engineering milestones across Big Tech, transforms them into captivating multi-modal visual assets (Manim motion graphics, 1080x1350 PDF carousels, and authentic developer copy), and delivers ready-to-publish packages to the creator's phone with 1-tap deployment.

---

## 📅 Phased Roadmap

```
Phase 1: Multi-Agent MVP (COMPLETED)
   ├── Core multi-agent pipeline (Strategist + Critic review loop)
   ├── Discord 2-way mobile studio & gateway poller
   ├── 12 elevated high-stakes production topics
   ├── 1080x1350 PDF Carousel Builder & 1080x1080 Manim base scene
   └── GitHub Actions CI/CD (Bandit security + CodeRabbit AI review)
   │
   ▼
Phase 2: Visual Excellence & Rich Diagrammatic Carousels (CURRENT FOCUS)
   ├── Zero font tofu glyphs: replace Unicode emojis with vector shapes
   ├── Visual comparison cards (e.g. UUIDv4 Random Split vs UUIDv7 Append)
   ├── Dynamic word-boundary text wrapping (zero mid-word string clipping)
   ├── Adaptive vertical canvas balancing (eliminating empty space on 2-item slides)
   └── Topic-aware emotional color palettes (Alert Coral, Emerald Green, Postgres Blue)
   │
   ▼
Phase 3: Autonomous Incident Watchdog & Trend Radar (NEXT)
   ├── Automated RSS & web watcher for Big Tech post-mortems (Cloudflare, Discord, AWS)
   ├── Auto-generating breaking incident carousels within 1 hour of public disclosure
   └── Incident timeline visual generator (e.g. 14:02 UTC alert -> 14:15 failover)
   │
   ▼
Phase 4: Multi-Platform Syndication & Closed-Loop Analytics (FUTURE)
   ├── Direct LinkedIn scheduled publishing with automated first-comment links
   ├── Cross-compiler transforming carousel slides into Twitter/X threads
   └── Engagement analytics tracker feeding winning hooks back into Content Strategist
```

---

## 🎯 Milestone Breakdown

### ✅ Phase 1: Multi-Agent MVP & Foundation *(Shipped)*
* [x] **Universal Collision-Free Grid:** Implemented in `src/design_system/rules.py` with `MANIM_BOTTOM_SAFE_LIMIT = -1.8` and AABB mathematical collision bounding boxes.
* [x] **Multi-Agent Think Tank:** Content Strategist and Staff Engineer Critic agents in `src/agents/` with automated refinement when appeal score < 8.8.
* [x] **Elevated 12 Topics:** Replaced textbook definitions with viral incident war stories (e.g. Read Replica Lag, 10M Sockets Reconnect Storms, Postgres MVCC Vacuum Bloat).
* [x] **Interactive Discord UI:** Dropdown selectors, 1-tap generation buttons, dynamic topic rerolling, and bounded LRU message cache.
* [x] **Production CI/CD:** GitHub Actions workflow with zero-leak secret guard, Bandit AST security scan, Flake8 syntax checks, and 39/39 passing tests.

### 🔄 Phase 2: Visual Excellence & Rich Diagrams *(In Progress)*
* [ ] **Eliminate All Font Tofu (`[]`):** Replace unrenderable emoji characters with programmatically drawn vector shapes (crisp arrows, checkmarks, status pills).
* [ ] **Visual Before/After Architecture Cards:** Introduce side-by-side comparative diagrams into the PDF carousel generator (e.g., comparing UUIDv4 vs UUIDv7 disk storage layouts).
* [ ] **Smart Typography Wrap:** Replace raw slice cutoffs (`[:32]`, `[:50]`) with font-aware bounding-box line wrapping to eliminate mid-word truncations.
* [ ] **Adaptive Vertical Balancing:** Dynamically expand card heights, font sizes, and spacing when a slide has fewer bullet points to eliminate barren dead space.
* [ ] **Context-Aware Takeaways:** Replace generic boilerplate with topic-accurate operational rules.

### 🚀 Phase 3: Autonomous Incident Watchdog *(Upcoming)*
* [ ] **Automated Tech Radar:** RSS ingest for Netflix TechBlog, Cloudflare Blog, Discord Engineering, and AWS Status dashboard.
* [ ] **Breaking Incident Auto-Drafts:** When a major service outage occurs, automatically draft a post-mortem breakdown and notify Discord.
* [ ] **Architecture Schematic Generator:** Programmatic generation of sequence diagrams and failure flowcharts directly in Pillow/SVG.

### 🌐 Phase 4: Multi-Platform Syndication & Feedback Loop *(Long-Term)*
* [ ] **Direct LinkedIn API Scheduled Publishing:** Scheduled morning release with automated first-comment resource links.
* [ ] **Twitter/X Thread Formatter:** Auto-generating 280-character thread progressions from carousel slides.
* [ ] **Closed-Loop Feedback:** Scraping LinkedIn post impression and engagement metrics to auto-tune the Content Strategist's future topic weights.

---

## 🛑 Scope Boundaries (In-Scope vs. Out-of-Scope)

| Feature | Status | Justification |
| :--- | :--- | :--- |
| **High-stakes distributed systems content** | **IN SCOPE** | Core value proposition; captures senior engineering attention. |
| **PDF Carousels & Manim 2D Animations** | **IN SCOPE** | Highest-reach formats on modern technical LinkedIn. |
| **Discord Mobile Studio** | **IN SCOPE** | Lowest friction for creator review and on-the-go publishing. |
| **Heavyweight Agent Frameworks (CrewAI, LangChain)** | **OUT OF SCOPE** | Adds 80+ redundant dependencies, breaks maintainability, violates Ponytail minimalism. |
| **Generic Motivational / Non-Tech Content** | **OUT OF SCOPE** | Dilutes brand authority and repels senior engineers. |
| **Aggressive Feed Scraping / Auto-DMs** | **OUT OF SCOPE** | Violates LinkedIn terms of service and risks account restriction. |
