"""Action engine — orchestrates Gemini analysis with Maps data."""

from __future__ import annotations

import logging
from typing import Callable, Optional

from app.models import ActionCard, AnalysisResult, NearbyPlace
from app import gemini_service, maps_service

logger = logging.getLogger(__name__)

# Severity ordering for sorting
SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


def _normalize_severity(severity: str) -> str:
    """Normalize severity string to one of the valid levels."""
    s = severity.strip().upper()
    if s in SEVERITY_ORDER:
        return s
    return "MEDIUM"


def sort_actions_by_severity(actions: list[ActionCard]) -> list[ActionCard]:
    """Sort actions by severity (most urgent first), preserving order within same level."""
    return sorted(actions, key=lambda a: SEVERITY_ORDER.get(a.severity, 2))


def process_text(
    text: str,
    status_callback: Optional[Callable[[str], None]] = None,
) -> AnalysisResult:
    """Process unstructured text input end-to-end.

    1. Send text to Gemini for analysis.
    2. Normalize severity levels.
    3. Sort actions by urgency.
    """
    result = gemini_service.analyze_text(text, status_callback=status_callback)
    result.severity = _normalize_severity(result.severity)
    for action in result.actions:
        action.severity = _normalize_severity(action.severity)
    result.actions = sort_actions_by_severity(result.actions)
    return result


def process_image(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    context: str = "",
    status_callback: Optional[Callable[[str], None]] = None,
) -> AnalysisResult:
    """Process an image input end-to-end."""
    result = gemini_service.analyze_image(
        image_bytes, mime_type, context, status_callback=status_callback
    )
    result.severity = _normalize_severity(result.severity)
    for action in result.actions:
        action.severity = _normalize_severity(action.severity)
    result.actions = sort_actions_by_severity(result.actions)
    return result


def process_audio(
    audio_bytes: bytes,
    mime_type: str = "audio/wav",
    context: str = "",
    status_callback: Optional[Callable[[str], None]] = None,
) -> AnalysisResult:
    """Process an audio input end-to-end."""
    result = gemini_service.analyze_audio(
        audio_bytes, mime_type, context, status_callback=status_callback
    )
    result.severity = _normalize_severity(result.severity)
    for action in result.actions:
        action.severity = _normalize_severity(action.severity)
    result.actions = sort_actions_by_severity(result.actions)
    return result


def enrich_with_nearby_services(
    result: AnalysisResult,
    lat: float,
    lng: float,
    service_type: str = "hospital",
) -> list[NearbyPlace]:
    """Find nearby services relevant to the analysis result.

    Args:
        result: The analysis result (used to determine service type if not provided).
        lat: User latitude.
        lng: User longitude.
        service_type: Override service type, otherwise inferred from result category.

    Returns:
        List of nearby places.
    """
    return maps_service.find_nearby(lat, lng, service_type)
