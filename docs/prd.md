# 📑 Product Requirements Document (PRD)

**Project Name:** LinkedIn Automation Studio  
**Target Platform:** LinkedIn, Discord (Control Room), GitHub  
**Status:** Live / Active Production  
**Owner:** Ahmed Hussain ([@ahmed-husssain](https://github.com/ahmed-husssain))  

---

## 1. Executive Summary

**LinkedIn Automation Studio** is an autonomous, multi-agent media production engine designed to create top 1% system architecture and backend engineering content for LinkedIn. 

Instead of generating generic, textbook AI summaries that senior engineers scroll past, the studio produces authentic, incident-driven engineering war stories and visual mental models. Every post package is delivered in seconds directly to a private Discord channel with 1-tap mobile review, downloadable 60fps videos, and vertical PDF carousel document decks.

---

## 2. Problem Statement

1. **Textbook Content Fatigue:** The internet is flooded with generic AI summaries (*"What is an array?"*, *"Why APIs matter"*). Senior and staff engineers tune out elementary explanations.
2. **High Asset Creation Friction:** Producing high-retention visual assets (60fps code animations, multi-page document carousels, architecture schematics) takes 4 to 6 hours per post in Blender, Figma, or Premiere.
3. **Corporate AI Cliché Saturation:** Most automated tools output obvious AI tropes (*"In today's fast-paced world, delve into the game-changer..."*), instantly destroying author credibility.
4. **Algorithmic Underperformance:** Text-only LinkedIn posts receive minimal distribution compared to **Document Carousels (3x algorithmic reach)** and **Video Motion Graphics**.

---

## 3. Target Audience & Personas

* **Primary Persona — Senior Backend / Distributed Systems Engineer:**
  * Values authentic battle scars, latency figures, production trade-offs, and counter-intuitive bugs.
  * Engages enthusiastically in the comments when asked specific architectural questions (e.g. partition sizing, TTL strategies, replication lag).
* **Secondary Persona — Founder / Tech Lead Building in Public:**
  * Needs a consistent, top-tier daily publishing cadence on LinkedIn without spending hours in design tools.

---

## 4. The 4 Core Output Modalities

Every topic or user prompt can be transformed into four distinct, production-ready formats:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        4 Core Output Modalities                        │
├────────────────────┬────────────────────┬──────────────────────────────┤
│ 1. PDF Carousel    │ 1080x1350 (4:5)    │ 6-slide dark-mode document   │
│                    │ Vertical Deck      │ deck for 3x LinkedIn reach   │
├────────────────────┼────────────────────┼──────────────────────────────┤
│ 2. Motion Video    │ 1080x1080 (1:1)    │ 15s 60fps 2D code animation  │
│                    │ Square MP4         │ with safe HUD margins        │
├────────────────────┼────────────────────┼──────────────────────────────┤
│ 3. Architecture    │ 1080x1080 (1:1)    │ Dynamic vector palette cover │
│    Diagram         │ PNG Cover          │ (Cyan, Emerald, Amber, Neon) │
├────────────────────┼────────────────────┼──────────────────────────────┤
│ 4. Developer Copy  │ Markdown Text      │ Hook + 3-step mental model + │
│                    │ Post Draft         │ Senior debate discussion     │
└────────────────────┴────────────────────┴──────────────────────────────┘
```

---

## 5. Feature Requirements & User Stories

### 5.1 Dynamic AI Topic Discovery
* **User Story:** As a user, I want the bot to brainstorm viral, top 1% distributed systems topics so that I never run out of compelling content.
* **Requirements:**
  * Must focus on real-world production incidents, Big Tech post-mortems (Netflix, Discord, Stripe, Uber), and counter-intuitive bugs.
  * Must provide 1-tap interactive buttons to immediately generate a **Video**, **PDF Carousel**, or discover **3 More Topics**.

### 5.2 Interactive Discord Control Room (Mobile First)
* **User Story:** As a creator on the go, I want to review, re-roll, and approve content from my phone inside Discord.
* **Requirements:**
  * Zero-latency response (< 2s).
  * Dropdowns with 2-line wrapped text preventing awkward string truncations.
  * Natural language dispatching: users can type topic names, ask technical questions, or give feedback.

### 5.3 Multi-Agent Editorial Pipeline
* **User Story:** As a publisher, I need automated fact-checking and quality control so that inaccurate claims never make it into production.
* **Requirements:**
  * **Content Strategist:** Drafts hook, 3-step visual mechanics, and senior questions.
  * **Staff Engineer Critic:** Fact-checks mechanics, calculates a `senior_appeal_score` (target $\ge 8.8$), and triggers iterative refinement if under threshold.
  * **Anti-AI Buzzword Penalizer:** Heavily penalizes banned corporate words (*"delve"*, *"unlock"*, *"game-changer"*, *"testament"*, *"tapestry"*).

### 5.4 Account Safety & Rate Limiting
* **User Story:** As a LinkedIn account owner, I must never have my account flagged or restricted for aggressive spamming.
* **Requirements:**
  * Strict maximum of **1 post per 20 hours**.
  * Atomic state persistence using safe file replacement to prevent 0-byte state corruptions.
  * Safe simulation fallback when direct API credentials are not provided.

---

## 6. Non-Functional Requirements & Invariants

1. **Universal Collision-Free Visuals:**
   * Videos: Bottom 2.2 coordinate units strictly reserved ($Y \ge -1.8$) so video player scrubbers never obscure text.
   * Carousels: Text wrapped strictly at word boundaries (`wrap_text_cleanly`). No raw mid-word string slicing.
   * Font Glyph Safety: Zero unrenderable Unicode emojis in PIL (no `[]` tofu boxes).
2. **Resource & Memory Safety:**
   * In-memory caches must use bounded LRU structures (`BoundedMessageTracker` max 1,000 items) to guarantee zero memory leaks in 24/7 daemon runs.
3. **Security:**
   * Zero secrets or tokens in code or Git history.
   * All credentials loaded strictly from `.env` via `settings.py`.

---

## 7. Anti-Goals (What We Explicitly Do NOT Build)

* ❌ **No Generic Motivational Content:** No inspirational quotes, life lessons, or non-technical spam.
* ❌ **No Heavy, Opaque Frameworks:** No CrewAI, LangChain, or APScheduler. All agent coordination and scheduling use native Python loops and stdlib.
* ❌ **No Headless Web Scraping of Private Profiles:** The tool does not scrape private LinkedIn users or violate platform terms.

---

## 8. Success Metrics & KPIs

* **Test Suite Pass Rate:** 100% (currently 39/39 passing).
* **Delivery Latency:** < 2 seconds for pre-rendered video/image assets; < 8 seconds for AI carousel compilation.
* **Senior Appeal Score:** Critic agent rating $\ge 8.8 / 10$ on all drafted posts.
* **Audience Engagement:** Minimum 3x reach on LinkedIn document carousel uploads compared to text-only baselines.
