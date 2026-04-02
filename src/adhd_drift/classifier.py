"""5-tier drift classification for ADHD conversation patterns."""

from __future__ import annotations

from adhd_drift.types import DriftClassification, ToleranceProfile


def classify_drift(
    score: float,
    profile: ToleranceProfile | None = None,
) -> DriftClassification:
    """Classify a drift score into one of 5 tiers.

    Boundaries are configurable via ToleranceProfile. Defaults:
        [0.0, 0.1) = ANCHORED
        [0.1, 0.3) = BRANCHING
        [0.3, 0.6) = TANGENT
        [0.6, 0.8) = WANDERING
        [0.8, 1.0] = DEEP_SHIFT
    """
    if profile is None:
        profile = ToleranceProfile.standard()

    b1, b2, b3, b4 = profile.classification_boundaries

    if score < b1:
        return DriftClassification.ANCHORED
    elif score < b2:
        return DriftClassification.BRANCHING
    elif score < b3:
        return DriftClassification.TANGENT
    elif score < b4:
        return DriftClassification.WANDERING
    else:
        return DriftClassification.DEEP_SHIFT


def is_alert(score: float, profile: ToleranceProfile) -> bool:
    """Check if a drift score exceeds the profile's alert threshold."""
    return score > profile.alert_threshold
