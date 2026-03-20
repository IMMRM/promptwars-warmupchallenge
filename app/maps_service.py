"""Google Maps Platform service — nearby places and directions."""

from __future__ import annotations

import re
import logging

import httpx
import streamlit as st

from app.config import get_maps_api_key
from app.models import NearbyPlace
from app.exceptions import MapsAPIError

logger = logging.getLogger(__name__)

PLACES_NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"

# Map logical service types to Google Maps place types
SERVICE_TYPE_MAP = {
    "hospital": "hospital",
    "pharmacy": "pharmacy",
    "fire_station": "fire_station",
    "police": "police",
    "shelter": "lodging",  # closest approximation
    "none": None,
}


def find_nearby(
    lat: float,
    lng: float,
    service_type: str = "hospital",
    radius_m: int = 5000,
    max_results: int = 5,
) -> list[NearbyPlace]:
    """Find nearby services using Google Maps Places API.

    Args:
        lat: Latitude of the user's location.
        lng: Longitude of the user's location.
        service_type: Logical type (hospital, pharmacy, fire_station, police, shelter).
        radius_m: Search radius in metres.
        max_results: Maximum number of results to return.

    Returns:
        List of NearbyPlace objects sorted by proximity.
    """
    api_key = get_maps_api_key()
    if not api_key:
        raise MapsAPIError("Google Maps API key is missing from .env.")

    place_type = SERVICE_TYPE_MAP.get(service_type, "hospital")
    if place_type is None:
        return []

    params = {
        "location": f"{lat},{lng}",
        "radius": radius_m,
        "type": place_type,
        "key": api_key,
    }

    try:
        resp = httpx.get(PLACES_NEARBY_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as exc:
        error_msg = f"Network or HTTP error: {exc}"
        logger.error("Places API request failed: %s", exc)
        raise MapsAPIError(error_msg)

    if data.get("status") not in ("OK", "ZERO_RESULTS"):
        status = data.get("status")
        error_msg = data.get("error_message", "Unknown error from Maps API")
        logger.error("Places API error: %s - %s", status, error_msg)
        raise MapsAPIError(f"Google Maps API ({status}): {error_msg}")

    places: list[NearbyPlace] = []
    for result in data.get("results", [])[:max_results]:
        loc = result.get("geometry", {}).get("location", {})
        places.append(
            NearbyPlace(
                name=result.get("name", "Unknown"),
                address=result.get("vicinity", ""),
                lat=loc.get("lat", 0),
                lng=loc.get("lng", 0),
                place_type=service_type,
                rating=result.get("rating"),
            )
        )

    return places


@st.cache_data(ttl=900, show_spinner=False)
def get_directions(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
) -> dict:
    """Get driving directions between two points.

    Returns:
        Dict with keys: distance_text, duration_text, steps (list of instruction strings).
    """
    api_key = get_maps_api_key()
    if not api_key:
        return {"distance_text": "", "duration_text": "", "steps": []}

    params = {
        "origin": f"{origin_lat},{origin_lng}",
        "destination": f"{dest_lat},{dest_lng}",
        "mode": "driving",
        "key": api_key,
    }

    try:
        resp = httpx.get(DIRECTIONS_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as exc:
        logger.error("Directions API request failed: %s", exc)
        return {"distance_text": "", "duration_text": "", "steps": []}

    if data.get("status") != "OK" or not data.get("routes"):
        return {"distance_text": "", "duration_text": "", "steps": []}

    leg = data["routes"][0]["legs"][0]
    steps = []
    for step in leg.get("steps", []):
        instruction = step.get("html_instructions", "")
        # Strip HTML tags for clean text
        clean = re.sub(r"<[^>]+>", "", instruction)
        steps.append(clean)

    return {
        "distance_text": leg.get("distance", {}).get("text", ""),
        "duration_text": leg.get("duration", {}).get("text", ""),
        "steps": steps,
    }
