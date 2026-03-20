"""Application configuration — loads and validates environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


def get_gemini_api_key() -> str:
    """Return the Gemini API key or raise if missing."""
    key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. "
            "Please add it to your .env file (see .env.example)."
        )
    return key


def get_maps_api_key() -> str:
    """Return the Google Maps API key or empty string if not configured."""
    return os.getenv("GOOGLE_MAPS_API_KEY", "")


# ── App constants ──────────────────────────────────────────────────────
APP_TITLE = "LifeLine AI"
APP_ICON = "🚨"
APP_DESCRIPTION = (
    "Turn messy, real-world inputs into structured, "
    "verified, life-saving action plans — instantly."
)

SEVERITY_COLORS = {
    "CRITICAL": "#FF4B4B",
    "HIGH": "#FF8C00",
    "MEDIUM": "#FFD700",
    "LOW": "#00C851",
}

SEVERITY_ICONS = {
    "CRITICAL": "🔴",
    "HIGH": "🟠",
    "MEDIUM": "🟡",
    "LOW": "🟢",
}
