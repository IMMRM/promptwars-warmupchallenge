"""Unit tests for action_engine module."""

import pytest
from app.models import ActionCard, AnalysisResult
from app.action_engine import sort_actions_by_severity, _normalize_severity


# ── Tests for severity normalization ───────────────────────────────────


class TestNormalizeSeverity:
    """Tests for _normalize_severity helper."""

    def test_valid_critical(self):
        assert _normalize_severity("CRITICAL") == "CRITICAL"

    def test_valid_high(self):
        assert _normalize_severity("HIGH") == "HIGH"

    def test_valid_medium(self):
        assert _normalize_severity("MEDIUM") == "MEDIUM"

    def test_valid_low(self):
        assert _normalize_severity("LOW") == "LOW"

    def test_lowercase_input(self):
        assert _normalize_severity("critical") == "CRITICAL"

    def test_mixed_case(self):
        assert _normalize_severity("High") == "HIGH"

    def test_with_whitespace(self):
        assert _normalize_severity("  LOW  ") == "LOW"

    def test_invalid_returns_medium(self):
        assert _normalize_severity("UNKNOWN") == "MEDIUM"

    def test_empty_returns_medium(self):
        assert _normalize_severity("") == "MEDIUM"


# ── Tests for action sorting ──────────────────────────────────────────


class TestSortActionsBySeverity:
    """Tests for sort_actions_by_severity."""

    def _make_action(self, severity: str, title: str = "Test") -> ActionCard:
        return ActionCard(
            title=title,
            description="desc",
            severity=severity,
            category="Test",
        )

    def test_already_sorted(self):
        actions = [
            self._make_action("CRITICAL", "A"),
            self._make_action("HIGH", "B"),
            self._make_action("LOW", "C"),
        ]
        sorted_actions = sort_actions_by_severity(actions)
        assert [a.title for a in sorted_actions] == ["A", "B", "C"]

    def test_reverse_order(self):
        actions = [
            self._make_action("LOW", "C"),
            self._make_action("HIGH", "B"),
            self._make_action("CRITICAL", "A"),
        ]
        sorted_actions = sort_actions_by_severity(actions)
        assert [a.severity for a in sorted_actions] == ["CRITICAL", "HIGH", "LOW"]

    def test_same_severity_preserves_order(self):
        actions = [
            self._make_action("HIGH", "First"),
            self._make_action("HIGH", "Second"),
        ]
        sorted_actions = sort_actions_by_severity(actions)
        assert [a.title for a in sorted_actions] == ["First", "Second"]

    def test_empty_list(self):
        assert sort_actions_by_severity([]) == []

    def test_single_action(self):
        actions = [self._make_action("MEDIUM", "Only")]
        sorted_actions = sort_actions_by_severity(actions)
        assert len(sorted_actions) == 1
        assert sorted_actions[0].title == "Only"

    def test_all_severities(self):
        actions = [
            self._make_action("MEDIUM", "M"),
            self._make_action("CRITICAL", "C"),
            self._make_action("LOW", "L"),
            self._make_action("HIGH", "H"),
        ]
        sorted_actions = sort_actions_by_severity(actions)
        assert [a.severity for a in sorted_actions] == [
            "CRITICAL",
            "HIGH",
            "MEDIUM",
            "LOW",
        ]


# ── Tests for data models ─────────────────────────────────────────────


class TestModels:
    """Tests for data model construction."""

    def test_action_card_defaults(self):
        card = ActionCard(
            title="Test", description="Desc", severity="HIGH", category="Medical"
        )
        assert card.steps == []
        assert card.verification == ""
        assert card.time_sensitive is False

    def test_action_card_with_steps(self):
        card = ActionCard(
            title="Test",
            description="Desc",
            severity="CRITICAL",
            category="Medical",
            steps=["Step 1", "Step 2"],
            time_sensitive=True,
        )
        assert len(card.steps) == 2
        assert card.time_sensitive is True

    def test_analysis_result_defaults(self):
        result = AnalysisResult(
            summary="Test summary",
            category="Medical",
            severity="HIGH",
        )
        assert result.key_facts == []
        assert result.actions == []
        assert result.raw_input_type == "text"

    def test_analysis_result_with_actions(self):
        action = ActionCard(
            title="Act", description="Desc", severity="HIGH", category="Medical"
        )
        result = AnalysisResult(
            summary="Summary",
            category="Emergency",
            severity="CRITICAL",
            key_facts=["Fact 1"],
            actions=[action],
        )
        assert len(result.actions) == 1
        assert result.key_facts == ["Fact 1"]
