# 🤖 Multi-Agent Think Tank & Role Specifications

## 1. Multi-Agent Philosophy

In **LinkedIn Automation Studio**, content generation is not treated as a single prompt-response call. Single-prompt generation frequently results in generic AI buzzwords (*"In today's fast-paced digital era..."*), superficial listicles, and visually unbalanced slides.

Instead, the studio employs a **Multi-Agent Think Tank** with an adversarial peer-review loop:
1. **The Strategist** generates ambitious, high-retention technical concepts and structural breakdowns.
2. **The Critic** acts as a battle-hardened Staff Software Engineer, scoring the plan against rigorous engineering criteria and rejecting weak or fluffy content.
3. **The Orchestrator** manages the feedback iteration loop, ensuring content is iteratively polished before any pixels or PDF pages are rendered.

```mermaid
flowchart TD
    UserPrompt["💡 User Prompt / Topic Trigger"] --> Orchestrator["Agent Orchestrator (orchestrator.py)"]
    
    subgraph ThinkTankLoop["Adversarial Peer-Review Loop"]
        Orchestrator -->|1. Request Strategy| Strategist["Staff Content Strategist (strategist.py)"]
        Strategist -->|2. Draft CarouselPlan / CopyPlan| Orchestrator
        Orchestrator -->|3. Submit Plan for Review| Critic["Staff Engineer Critic (critic.py)"]
        Critic -->|4. Return Score & Critiques| Orchestrator
        
        Orchestrator -- "Score < 80 (Iter <= 2)" -->|5. Refinement with Feedback| Strategist
    end
    
    Orchestrator -- "Score >= 80 or Max Iter" --> Downstream["Downstream Rendering Engines"]
    Downstream --> CarouselBuilder["Carousel Builder (carousel_builder.py)"]
    Downstream --> DiagramEngine["Diagram Engine (diagram_engine.py)"]
    Downstream --> CopyEngine["Post Copy Engine (copy_engine.py)"]
```

---

## 2. Agent Roster & Personas

### 2.1 The Content Strategist (`StrategistAgent`)
* **File:** [`src/agents/strategist.py`](file:///D:/LinkedInAutomationStudio/src/agents/strategist.py)
* **Model:** Google Gemini 2.5 Flash (via `google-genai` SDK)
* **Persona:** Senior Technical Content Strategist & Developer Advocate with 10+ years in distributed systems engineering.
* **Core Responsibilities:**
  - Deconstructs complex distributed systems concepts (e.g. Raft consensus, Kafka partitions, Idempotency keys, LSM trees) into logical, digestible slides.
  - Crafts punchy, pattern-interrupting hooks designed for mobile feeds.
  - Structures vertical 4:5 slides into a coherent narrative: *The Problem $\to$ The Naive Mistake $\to$ The Core Mechanism $\to$ The Deep Dive $\to$ Tradeoffs & Production Rules*.
* **Strict Directives:**
  - **No Buzzword Openers:** Never start with *"Have you ever wondered..."*, *"In today's world..."*, or *"Let's dive in"*.
  - **Concrete Numbers & Code:** Prefer concrete latency/throughput metrics (e.g. *"reduced p99 from 420ms to 18ms"*) over vague promises (*"greatly improved speed"*).
  - **Pacing:** Each slide must have exactly 1 core takeaway. Do not overload slides with multiple competing concepts.

### 2.2 The Staff Engineer Critic (`CriticAgent`)
* **File:** [`src/agents/critic.py`](file:///D:/LinkedInAutomationStudio/src/agents/critic.py)
* **Model:** Google Gemini 2.5 Flash (Temperature: 0.2 for strict deterministic evaluation)
* **Persona:** Skeptical Staff Infrastructure Engineer and Code Reviewer.
* **Core Responsibilities:**
  - Evaluates generated plans across 4 weighted scoring dimensions:
    1. **Hook Strength (25%):** Does the hook stop a scrolling senior engineer within 1.5 seconds?
    2. **Value Density (30%):** Is there high signal-to-noise ratio, or is it filler text?
    3. **Engineering Credibility (25%):** Are failure modes, edge cases, and architectural tradeoffs acknowledged?
    4. **Visual Pacing (20%):** Can each slide be understood visually in under 5 seconds?
  - Provides an overall score (0–100) and actionable, bulleted critique directives.
  - If score $< 80$, explicitly flags what must be removed, condensed, or technically clarified.

### 2.3 The Agent Orchestrator (`AgentOrchestrator`)
* **File:** [`src/agents/orchestrator.py`](file:///D:/LinkedInAutomationStudio/src/agents/orchestrator.py)
* **Persona:** Autonomous Pipeline Manager.
* **Core Responsibilities:**
  - Manages the lifecycle of content synthesis requests.
  - Runs the auto-refinement loop: feeds the Critic's specific feedback back into the Strategist for targeted revisions.
  - Limits iterations to a maximum of 2 passes to bound latency and token consumption.
  - Provides deterministic fallbacks if API limits or parsing errors occur.

### 2.4 The Carousel Builder (`CarouselBuilder`)
* **File:** [`src/agents/carousel_builder.py`](file:///D:/LinkedInAutomationStudio/src/agents/carousel_builder.py)
* **Persona:** Precision Graphic Designer & Typesetter.
* **Core Responsibilities:**
  - Translates Pydantic `CarouselPlan` JSON into pixel-perfect 1080x1350 multi-page PDF documents.
  - Renders modern dark-mode aesthetic cards with dynamic accent colors.
  - Enforces the **Zero Font Tofu Rule**: Renders native vector shapes (PIL `draw.line`, `draw.polygon`) or ASCII arrows (`->`, `>>`) instead of missing Unicode emoji glyphs (`[]`).

### 2.5 The Motion Graphics Designer (`MotionEngine`)
* **Files:** [`src/animations/`](file:///D:/LinkedInAutomationStudio/src/animations/)
* **Engine:** Manim Community Edition (CE v0.22.0)
* **Core Responsibilities:**
  - Renders 1080x1080 60fps MP4 video animations explaining system mechanics.
  - Enforces the **Manim HUD Safe Zone**: All active diagram objects, nodes, and text must strictly stay in coordinate space $Y \ge -1.8$. The region $Y \in [-3.6, -1.8]$ is reserved for the bottom progress scrubber and branding watermark.

---

## 3. Data Contracts & Pydantic v2 Schemas

All inter-agent communication is governed by typed Pydantic v2 models in [`src/agents/schemas.py`](file:///D:/LinkedInAutomationStudio/src/agents/schemas.py):

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class SlidePlan(BaseModel):
    """Schema for an individual carousel slide."""
    slide_number: int = Field(..., ge=1, le=10, description="1-indexed slide number")
    title: str = Field(..., min_length=3, max_length=60, description="Bold slide header")
    subtitle: Optional[str] = Field(None, max_length=90, description="Contextual subhead")
    body_points: List[str] = Field(..., min_items=1, max_items=4, description="High-signal bullet points")
    card_highlight: Optional[str] = Field(None, max_length=120, description="Visual callout card content")
    slide_type: str = Field("content", description="cover | problem | mechanism | deep_dive | summary")

class CarouselPlan(BaseModel):
    """Schema for the full multi-slide carousel presentation."""
    topic: str = Field(..., min_length=3, max_length=80)
    hook: str = Field(..., min_length=10, max_length=120, description="Viral pattern-interrupt headline")
    target_audience: str = Field(..., description="Target reader persona, e.g. Backend Engineers")
    color_theme: str = Field("slate", description="slate | navy | obsidian | cyberpunk | emerald")
    slides: List[SlidePlan] = Field(..., min_items=4, max_items=8)
    linkedin_copy: str = Field(..., min_length=50, max_length=1500, description="Formatted post copy")

class CriticEvaluation(BaseModel):
    """Schema for the Critic's adversarial review output."""
    overall_score: int = Field(..., ge=0, le=100, description="Composite score 0-100")
    hook_score: int = Field(..., ge=0, le=100)
    value_density_score: int = Field(..., ge=0, le=100)
    credibility_score: int = Field(..., ge=0, le=100)
    critiques: List[str] = Field(..., description="Actionable points of improvement")
    approved: bool = Field(..., description="True if overall_score >= 80")
```

---

## 4. Multi-Agent Refinement Protocol

When the Critic rejects a draft plan (`approved == False`):
1. **Targeted Diffing:** The Orchestrator constructs a refinement prompt containing:
   - The original `CarouselPlan` JSON.
   - The Critic's specific `critiques` list.
   - The dimension with the lowest sub-score (e.g. *Value Density: 65/100*).
2. **Constrained Correction:** The Strategist is instructed to modify *only* the flagged slides or copy, preserving approved components.
3. **Loop Termination:**
   - If iteration 2 is reached, the highest-scoring plan is selected.
   - If a schema parsing exception occurs, the system falls back to curated offline templates in [`src/config/topics.py`](file:///D:/LinkedInAutomationStudio/src/config/topics.py) to guarantee zero pipeline crashes.
