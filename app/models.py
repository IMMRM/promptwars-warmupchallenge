"""Data models used across the application."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ActionCard:
    """A single, prioritized action the user should take."""

    title: str
    description: str
    severity: str  # CRITICAL | HIGH | MEDIUM | LOW
    category: str  # e.g. "Medical", "Safety", "Navigation"
    steps: list[str] = field(default_factory=list)
    verification: str = ""
    time_sensitive: bool = False


@dataclass
class AnalysisResult:
    """Structured result from analysing unstructured input."""

    summary: str
    category: str  # Medical | Emergency | Weather | Safety | General
    severity: str  # CRITICAL | HIGH | MEDIUM | LOW
    key_facts: list[str] = field(default_factory=list)
    actions: list[ActionCard] = field(default_factory=list)
    raw_input_type: str = "text"  # text | image | audio
    verification_notes: str = ""


@dataclass
class NearbyPlace:
    """A nearby service found via Google Maps."""

    name: str
    address: str
    lat: float
    lng: float
    place_type: str  # hospital | pharmacy | fire_station | police
    rating: Optional[float] = None
    distance_text: str = ""
    duration_text: str = ""
