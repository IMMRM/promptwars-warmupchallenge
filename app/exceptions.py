"""Custom exceptions for LifeLine AI."""

class LifeLineError(Exception):
    """Base exception for all LifeLine AI application errors."""
    pass


class AIAnalysisError(LifeLineError):
    """Raised when the AI service fails to generate or parse an analysis."""
    pass


class MapsAPIError(LifeLineError):
    """Raised when the Google Maps API requests fail or return an error."""
    pass


class RateLimitError(AIAnalysisError):
    """Raised when the AI service exhausts all rate limit retries."""
    pass
