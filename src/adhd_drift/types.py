"""Shared types for ADHD drift visualizer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DriftClassification(Enum):
    """5-tier drift classification for conversation focus patterns."""

    ANCHORED = "anchored"
    BRANCHING = "branching"
    TANGENT = "tangent"
    WANDERING = "wandering"
    DEEP_SHIFT = "deep_shift"


@dataclass
class ToleranceProfile:
    """Configurable drift tolerance. Determines when alerts fire."""

    name: str
    max_acceptable_drift: float
    alert_threshold: float
    classification_boundaries: tuple[float, float, float, float] = (0.1, 0.3, 0.6, 0.8)

    @classmethod
    def strict(cls) -> ToleranceProfile:
        """Strict: flags any topic shift quickly."""
        return cls(name="strict", max_acceptable_drift=0.15, alert_threshold=0.10)

    @classmethod
    def standard(cls) -> ToleranceProfile:
        """Standard: normal conversation flow."""
        return cls(name="standard", max_acceptable_drift=0.30, alert_threshold=0.25)

    @classmethod
    def creative(cls) -> ToleranceProfile:
        """Creative: brainstorming mode, pivots expected."""
        return cls(name="creative", max_acceptable_drift=0.60, alert_threshold=0.50)

    @classmethod
    def freeform(cls) -> ToleranceProfile:
        """Freeform: stream of consciousness, no judgment."""
        return cls(name="freeform", max_acceptable_drift=0.80, alert_threshold=0.70)


@dataclass
class ChatMessage:
    """One message in a conversation — the raw input to the drift engine."""

    index: int
    text: str
    role: str = "user"
    topic_label: str = ""
    timestamp: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class SignalScores:
    """Individual signal contributions to the composite drift score."""

    semantic_distance: float = 0.0
    topic_divergence: float = 0.0
    specificity_shift: float = 0.0
    velocity: float = 0.0


@dataclass
class DriftScore:
    """Per-message drift analysis result."""

    step_index: int
    composite_score: float
    classification: DriftClassification
    signals: SignalScores
    cumulative_drift: float
    recovery_score: float
    topic_label: str = ""
    is_pivot: bool = False
    alert: bool = False
    suggestions: list[str] = field(default_factory=list)


@dataclass
class SessionReport:
    """Full session drift analysis."""

    steps: list[DriftScore]
    total_steps: int
    total_pivots: int
    peak_drift: float
    peak_drift_step: int
    mean_drift: float
    final_classification: DriftClassification
    drift_velocity_trend: str
    longest_focus_streak: int
    most_visited_topic: str
    topic_sequence: list[str] = field(default_factory=list)
    pivot_points: list[int] = field(default_factory=list)
    alerts: list[dict] = field(default_factory=list)
