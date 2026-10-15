"""
Strict Pydantic v2 schemas for LinkedIn Automation Studio.
Guarantees clean, typed contracts between LLM agents, copy formatting, and PDF rendering.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class SlideSchema(BaseModel):
    badge: str = Field(..., max_length=40, description="Short category badge (e.g., 'The Bottleneck')")
    title: str = Field(..., max_length=60, description="Slide main title")
    subtitle: str = Field(..., max_length=90, description="Slide supporting subtitle")
    bullets: List[str] = Field(..., min_length=1, max_length=5, description="1-5 punchy, high-retention bullet points")
    accent: str = Field(default="#58a6ff", description="Hex accent color code")
    layout_type: str = Field(default="standard", description="standard | comparison | code | metric")
    code_snippet: Optional[str] = Field(default=None, description="Optional configuration or code snippet")
    left_title: Optional[str] = Field(default=None, description="Optional title for comparison approach A")
    right_title: Optional[str] = Field(default=None, description="Optional title for comparison approach B")
    metric_label: Optional[str] = Field(default=None, description="Optional KPI title")
    metric_value: Optional[str] = Field(default=None, description="Optional big stat, e.g. 420ms -> 18ms")
    metric_delta: Optional[str] = Field(default=None, description="Optional improvement note")

    @field_validator("accent")
    @classmethod
    def validate_hex_color(cls, v: str) -> str:
        if not v.startswith("#") or len(v) != 7:
            return "#58a6ff"
        return v


class PostPackageSchema(BaseModel):
    topic_title: str = Field(..., max_length=80)
    subject: str = Field(..., max_length=60)
    hook: str = Field(..., min_length=20, max_length=350, description="High-retention incident or curiosity hook")
    body: str = Field(..., min_length=50, description="Step-by-step breakdown or mental model")
    senior_question: str = Field(..., min_length=15, max_length=250, description="Open-ended architectural debate question")
    slides: List[SlideSchema] = Field(..., min_length=3, max_length=8, description="Ordered slide deck")
    difficulty: str = Field(default="production", description="foundation | production | staff")


class CriticReviewSchema(BaseModel):
    technical_verdict: str = Field(..., description="Verdict on architecture and mechanics")
    senior_appeal_score: float = Field(..., ge=1.0, le=10.0, description="Scored from 1.0 to 10.0")
    strengths: List[str] = Field(default_factory=list)
    suggested_improvements: List[str] = Field(default_factory=list)
    approved: bool = Field(default=True)
