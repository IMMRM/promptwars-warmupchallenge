"""Gemini multimodal AI service — processes text, images, and audio transcriptions."""

from __future__ import annotations

import json
import time
import logging
from typing import Optional

from google import genai
from google.genai import types

from app.config import get_gemini_api_key
from app.models import ActionCard, AnalysisResult

logger = logging.getLogger(__name__)

# ── Model fallback chain ──────────────────────────────────────────────
# If the primary model is rate-limited, try the next one in the list.
MODEL_CHAIN = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite-preview-02-05", 
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
]

MAX_RETRIES = 3
INITIAL_BACKOFF_S = 5  # seconds before first retry

# ── System prompt for structured extraction ────────────────────────────
SYSTEM_PROMPT = """\
You are LifeLine AI, an expert emergency-response and health assistant.
Your job is to take UNSTRUCTURED, messy, real-world input and convert it into
STRUCTURED, actionable, life-saving information.

Analyze the input carefully and return a JSON object with EXACTLY this schema:

{
  "summary": "One-sentence summary of the situation",
  "category": "Medical | Emergency | Weather | Safety | General",
  "severity": "CRITICAL | HIGH | MEDIUM | LOW",
  "key_facts": ["fact1", "fact2", ...],
  "actions": [
    {
      "title": "Short action title",
      "description": "Detailed description of what to do",
      "severity": "CRITICAL | HIGH | MEDIUM | LOW",
      "category": "Medical | Safety | Navigation | Communication | Preparation",
      "steps": ["step1", "step2", ...],
      "verification": "How to verify this action was done correctly",
      "time_sensitive": true/false
    }
  ],
  "verification_notes": "Sources or reasoning used to verify the information",
  "suggested_service_type": "hospital | pharmacy | fire_station | police | shelter | none"
}

Rules:
1. Actions MUST be ordered by urgency (most urgent first).
2. For medical inputs, include dosage warnings, contraindication checks, and when to call emergency services.
3. For weather/disaster inputs, prioritize evacuation and safety.
4. For photos, describe what you observe and infer the appropriate response.
5. Always include a verification note explaining your reasoning.
6. Be specific and actionable — avoid vague advice.
7. If the situation is life-threatening, the FIRST action must be "Call Emergency Services" with the relevant number.
8. Return ONLY the JSON object, no markdown fences, no extra text.
"""


def _build_client() -> genai.Client:
    """Create a Gemini client using the configured API key."""
    api_key = get_gemini_api_key()
    return genai.Client(api_key=api_key)


def _parse_gemini_response(raw_text: str) -> dict:
    """Parse the JSON response from Gemini, handling markdown fences."""
    text = raw_text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last lines (fences)
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)


def _dict_to_result(data: dict, input_type: str) -> AnalysisResult:
    """Convert the parsed JSON dict into an AnalysisResult."""
    actions = []
    for a in data.get("actions", []):
        actions.append(
            ActionCard(
                title=a.get("title", "Action"),
                description=a.get("description", ""),
                severity=a.get("severity", "MEDIUM"),
                category=a.get("category", "General"),
                steps=a.get("steps", []),
                verification=a.get("verification", ""),
                time_sensitive=a.get("time_sensitive", False),
            )
        )
    return AnalysisResult(
        summary=data.get("summary", "Analysis complete."),
        category=data.get("category", "General"),
        severity=data.get("severity", "MEDIUM"),
        key_facts=data.get("key_facts", []),
        actions=actions,
        raw_input_type=input_type,
        verification_notes=data.get("verification_notes", ""),
    )


def _is_rate_limit_error(exc: Exception) -> bool:
    """Check if an exception is a 429 rate-limit / quota-exceeded error."""
    error_str = str(exc)
    return "429" in error_str or "RESOURCE_EXHAUSTED" in error_str


def _generate_with_retry(
    client: genai.Client,
    contents,
    config: types.GenerateContentConfig,
    status_callback=None,
):
    """Call Gemini with automatic retry + model fallback on rate limits.

    Tries each model in MODEL_CHAIN. For each model, retries up to MAX_RETRIES
    times with exponential backoff if a 429 error is received.

    Args:
        client: The Gemini client.
        contents: The content to send (text string, or list with Parts).
        config: GenerateContentConfig (system prompt, temperature, etc.).
        status_callback: Optional callable(msg: str) for progress updates.

    Returns:
        The GenerateContentResponse from the first successful call.

    Raises:
        The last exception encountered if all models and retries fail.
    """
    last_exc = None

    for model_name in MODEL_CHAIN:
        backoff = INITIAL_BACKOFF_S

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                if status_callback and (model_name != MODEL_CHAIN[0] or attempt > 1):
                    status_callback(
                        f"Trying {model_name} (attempt {attempt}/{MAX_RETRIES})..."
                    )

                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config,
                )
                logger.info("Success with model=%s on attempt %d", model_name, attempt)
                return response

            except Exception as exc:
                last_exc = exc
                if _is_rate_limit_error(exc):
                    logger.warning(
                        "Rate-limited on %s (attempt %d/%d). "
                        "Retrying in %ds...",
                        model_name,
                        attempt,
                        MAX_RETRIES,
                        backoff,
                    )
                    if status_callback:
                        status_callback(
                            f"⏳ Rate-limited on {model_name}. "
                            f"Retrying in {backoff}s..."
                        )
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 60)  # exponential, cap at 60s
                else:
                    # Non-rate-limit error (e.g. 404 model not found)
                    # Don't retry this model, skip immediately to the next one in the chain
                    logger.warning("Model %s failed with non-rate-limit error: %s. Skipping to next model.", model_name, str(exc))
                    if status_callback:
                        status_callback(f"⚠️ {model_name} not available, switching models...")
                    break  # Break out of the retry loop to try the next model

        else:
            # Exhausted retries for this model without breaking
            logger.warning("All retries exhausted for %s, trying next model.", model_name)

    # All models failed
    raise last_exc  # type: ignore[misc]


# ── Public API ─────────────────────────────────────────────────────────


def analyze_text(text: str, status_callback=None) -> AnalysisResult:
    """Analyze unstructured text input and return structured actions."""
    client = _build_client()
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.2,
    )
    response = _generate_with_retry(client, text, config, status_callback)
    data = _parse_gemini_response(response.text)
    return _dict_to_result(data, "text")


def analyze_image(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    additional_context: str = "",
    status_callback=None,
) -> AnalysisResult:
    """Analyze an uploaded image and return structured actions."""
    client = _build_client()

    prompt = (
        "Analyze this image and identify any emergency, health, safety, "
        "or actionable situation. Provide structured life-saving actions."
    )
    if additional_context:
        prompt += f"\n\nAdditional context from user: {additional_context}"

    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.2,
    )
    response = _generate_with_retry(
        client, [prompt, image_part], config, status_callback
    )
    data = _parse_gemini_response(response.text)
    return _dict_to_result(data, "image")


def analyze_audio(
    audio_bytes: bytes,
    mime_type: str = "audio/wav",
    additional_context: str = "",
    status_callback=None,
) -> AnalysisResult:
    """Analyze an uploaded audio file and return structured actions."""
    client = _build_client()

    prompt = (
        "This is an audio recording. Listen carefully, transcribe the content, "
        "and identify any emergency, health, safety, or actionable situation. "
        "Provide structured life-saving actions based on what you hear."
    )
    if additional_context:
        prompt += f"\n\nAdditional context from user: {additional_context}"

    audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.2,
    )
    response = _generate_with_retry(
        client, [prompt, audio_part], config, status_callback
    )
    data = _parse_gemini_response(response.text)
    return _dict_to_result(data, "audio")
