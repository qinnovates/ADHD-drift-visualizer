"""Integration tests for the ADHD drift engine."""

from __future__ import annotations

import pytest

from adhd_drift.types import (
    DriftClassification,
    ToleranceProfile,
)
from adhd_drift.classifier import classify_drift
from adhd_drift.tracker import (
    cumulative_drift,
    detect_pivot_points,
    drift_velocity_trend,
    longest_focus_streak,
)
from adhd_drift.scorer import SignalWeights, compute_velocity
from adhd_drift.topics import extract_topic_label


class TestClassifier:
    def test_anchored_score(self):
        assert classify_drift(0.05) == DriftClassification.ANCHORED

    def test_branching_score(self):
        assert classify_drift(0.2) == DriftClassification.BRANCHING

    def test_tangent_score(self):
        assert classify_drift(0.45) == DriftClassification.TANGENT

    def test_wandering_score(self):
        assert classify_drift(0.7) == DriftClassification.WANDERING

    def test_deep_shift_score(self):
        assert classify_drift(0.9) == DriftClassification.DEEP_SHIFT

    def test_custom_profile(self):
        profile = ToleranceProfile(
            name="tight",
            max_acceptable_drift=0.1,
            alert_threshold=0.05,
            classification_boundaries=(0.05, 0.15, 0.3, 0.5),
        )
        assert classify_drift(0.06, profile) == DriftClassification.BRANCHING
        assert classify_drift(0.4, profile) == DriftClassification.WANDERING


class TestTracker:
    def test_cumulative_drift_empty(self):
        assert cumulative_drift([]) == 0.0

    def test_cumulative_drift_single(self):
        assert cumulative_drift([0.5]) == 0.5

    def test_cumulative_drift_decay(self):
        scores = [0.8, 0.0, 0.0, 0.0, 0.0]
        result = cumulative_drift(scores)
        assert result < 0.8

    def test_detect_pivot_points(self):
        scores = [0.0, 0.1, 0.4, 0.5, 0.2, 0.7]
        pivots = detect_pivot_points(scores, velocity_threshold=0.12)
        assert 2 in pivots
        assert 5 in pivots

    def test_velocity_trend_stable(self):
        assert drift_velocity_trend([0.1, 0.1, 0.1]) == "stable"

    def test_velocity_trend_accelerating(self):
        assert drift_velocity_trend([0.1, 0.3, 0.6]) == "accelerating"

    def test_velocity_trend_refocused(self):
        assert drift_velocity_trend([0.5, 0.3, 0.05]) == "refocused"

    def test_longest_focus_streak(self):
        classifications = ["anchored", "anchored", "tangent", "anchored", "branching", "branching", "wandering"]
        assert longest_focus_streak(classifications) == 3


class TestScorer:
    def test_weights_validate(self):
        weights = SignalWeights()
        weights.validate()

    def test_weights_invalid(self):
        weights = SignalWeights(semantic_distance=0.9)
        with pytest.raises(ValueError):
            weights.validate()

    def test_velocity_no_history(self):
        assert compute_velocity(0.5, []) == 0.0

    def test_velocity_accelerating(self):
        vel = compute_velocity(0.8, [0.1, 0.3])
        assert vel > 0.0


class TestTopics:
    def test_extract_topic_label(self):
        label = extract_topic_label("Let's fix the authentication token refresh mechanism")
        assert len(label) > 0
        assert "the" not in label.split()

    def test_extract_topic_label_empty(self):
        assert extract_topic_label("") == "general"

    def test_extract_topic_label_short(self):
        assert extract_topic_label("ok") == "general"
