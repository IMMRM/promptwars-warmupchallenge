"""Integration tests for Gemini service JSON parsing."""

import json
import pytest
from app.gemini_service import _parse_gemini_response, _dict_to_result


# ── Tests for response parsing ─────────────────────────────────────────


class TestParseGeminiResponse:
    """Tests for _parse_gemini_response."""

    def test_plain_json(self):
        raw = json.dumps({"summary": "Test", "severity": "HIGH"})
        result = _parse_gemini_response(raw)
        assert result["summary"] == "Test"

    def test_json_with_markdown_fences(self):
        raw = '```json\n{"summary": "Test"}\n```'
        result = _parse_gemini_response(raw)
        assert result["summary"] == "Test"

    def test_json_with_plain_fences(self):
        raw = '```\n{"summary": "Test"}\n```'
        result = _parse_gemini_response(raw)
        assert result["summary"] == "Test"

    def test_json_with_whitespace(self):
        raw = '  \n  {"summary": "Test"}  \n  '
        result = _parse_gemini_response(raw)
        assert result["summary"] == "Test"

    def test_invalid_json_raises(self):
        with pytest.raises(json.JSONDecodeError):
            _parse_gemini_response("not json at all")


# ── Tests for dict-to-result conversion ────────────────────────────────


class TestDictToResult:
    """Tests for _dict_to_result."""

    def test_minimal_dict(self):
        data = {
            "summary": "Chest pain detected",
            "category": "Medical",
            "severity": "CRITICAL",
        }
        result = _dict_to_result(data, "text")
        assert result.summary == "Chest pain detected"
        assert result.category == "Medical"
        assert result.severity == "CRITICAL"
        assert result.raw_input_type == "text"
        assert result.actions == []

    def test_full_dict_with_actions(self):
        data = {
            "summary": "Emergency situation",
            "category": "Emergency",
            "severity": "HIGH",
            "key_facts": ["Fact 1", "Fact 2"],
            "actions": [
                {
                    "title": "Call 911",
                    "description": "Immediately call emergency services",
                    "severity": "CRITICAL",
                    "category": "Communication",
                    "steps": ["Pick up phone", "Dial 911"],
                    "verification": "Confirm dispatcher answers",
                    "time_sensitive": True,
                }
            ],
            "verification_notes": "Based on symptom analysis",
        }
        result = _dict_to_result(data, "image")
        assert result.raw_input_type == "image"
        assert len(result.actions) == 1
        assert result.actions[0].title == "Call 911"
        assert result.actions[0].time_sensitive is True
        assert len(result.actions[0].steps) == 2

    def test_missing_fields_use_defaults(self):
        data = {}
        result = _dict_to_result(data, "audio")
        assert result.summary == "Analysis complete."
        assert result.category == "General"
        assert result.severity == "MEDIUM"
        assert result.raw_input_type == "audio"
