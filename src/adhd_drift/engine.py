"""DriftEngine — main orchestrator for ADHD conversation drift analysis."""

from __future__ import annotations

import numpy as np

from adhd_drift.types import (
    ChatMessage,
    DriftClassification,
    DriftScore,
    SessionReport,
    SignalScores,
    ToleranceProfile,
)
from adhd_drift.scorer import (
    SignalWeights,
    compute_composite_score,
    compute_topic_divergence,
    compute_velocity,
)
from adhd_drift.classifier import classify_drift, is_alert
from adhd_drift.tracker import (
    cumulative_drift,
    detect_pivot_points,
    drift_velocity_trend,
    longest_focus_streak,
)
from adhd_drift.recovery import recovery_score, refocus_suggestions
from adhd_drift.signals import specificity_shift
from adhd_drift.topics import extract_topic_label, detect_topic_shift
from adhd_drift.embeddings import embed, cosine_distance


class DriftEngine:
    """Stateful drift analysis engine for a single chat session.

    Usage:
        engine = DriftEngine()
        engine.add_message(ChatMessage(index=0, text="Let's work on the auth module"))
        engine.add_message(ChatMessage(index=1, text="Oh wait, what about that CSS bug?"))
        report = engine.report()
    """

    def __init__(
        self,
        profile: ToleranceProfile | None = None,
        weights: SignalWeights | None = None,
    ):
        self._profile = profile or ToleranceProfile.standard()
        self._weights = weights or SignalWeights()
        self._weights.validate()

        self._messages: list[ChatMessage] = []
        self._scores: list[DriftScore] = []
        self._embeddings: list[np.ndarray] = []
        self._baseline_embedding: np.ndarray | None = None
        self._previous_embedding: np.ndarray | None = None
        self._steps_since_focused: int = 0

    @property
    def profile(self) -> ToleranceProfile:
        return self._profile

    @property
    def messages(self) -> list[ChatMessage]:
        return list(self._messages)

    @property
    def scores(self) -> list[DriftScore]:
        return list(self._scores)

    def add_message(self, message: ChatMessage) -> DriftScore:
        """Process a new message and return its drift score.

        The first message becomes the baseline topic. Subsequent messages are
        scored against the baseline using 4-signal triangulation.
        """
        msg_embedding = embed(message.text)
        self._embeddings.append(msg_embedding)
        self._messages.append(message)

        topic_label = message.topic_label or extract_topic_label(message.text)

        if self._baseline_embedding is None:
            self._baseline_embedding = msg_embedding
            self._previous_embedding = msg_embedding
            score = DriftScore(
                step_index=message.index,
                composite_score=0.0,
                classification=DriftClassification.ANCHORED,
                signals=SignalScores(),
                cumulative_drift=0.0,
                recovery_score=1.0,
                topic_label=topic_label,
            )
            self._scores.append(score)
            return score

        # Semantic distance: global drift from the original topic (vs baseline)
        sem_dist = cosine_distance(self._baseline_embedding, msg_embedding)
        # Topic divergence: local shift from previous message (different signal)
        topic_div = compute_topic_divergence(self._previous_embedding, msg_embedding)  # type: ignore[arg-type]
        spec_shift = specificity_shift(message)

        previous_composites = [s.composite_score for s in self._scores]
        preliminary_composite = (
            self._weights.semantic_distance * sem_dist
            + self._weights.topic_divergence * topic_div
            + self._weights.specificity_shift * spec_shift
        )
        vel = compute_velocity(preliminary_composite, previous_composites)

        signals = SignalScores(
            semantic_distance=sem_dist,
            topic_divergence=topic_div,
            specificity_shift=spec_shift,
            velocity=vel,
        )

        composite = compute_composite_score(signals, self._weights)
        classification = classify_drift(composite, self._profile)

        all_composites = previous_composites + [composite]
        cum_drift = cumulative_drift(all_composites)

        is_pivot = detect_topic_shift(msg_embedding, self._previous_embedding)  # type: ignore[arg-type]

        if classification == DriftClassification.ANCHORED:
            self._steps_since_focused = 0
        else:
            self._steps_since_focused += 1

        rec_score = recovery_score(composite, self._steps_since_focused)
        alert = is_alert(composite, self._profile)

        score = DriftScore(
            step_index=message.index,
            composite_score=round(composite, 4),
            classification=classification,
            signals=signals,
            cumulative_drift=round(cum_drift, 4),
            recovery_score=round(rec_score, 4),
            topic_label=topic_label,
            is_pivot=is_pivot,
            alert=alert,
        )

        score.suggestions = refocus_suggestions(message, score)

        self._scores.append(score)
        self._previous_embedding = msg_embedding
        return score

    def report(self) -> SessionReport:
        """Generate a full session report from all processed messages."""
        if not self._scores:
            return SessionReport(
                steps=[],
                total_steps=0,
                total_pivots=0,
                peak_drift=0.0,
                peak_drift_step=0,
                mean_drift=0.0,
                final_classification=DriftClassification.ANCHORED,
                drift_velocity_trend="stable",
                longest_focus_streak=0,
                most_visited_topic="none",
            )

        composites = [s.composite_score for s in self._scores]
        peak = max(composites)
        peak_idx = composites.index(peak)

        classifications = [s.classification.value for s in self._scores]
        topic_labels = [s.topic_label for s in self._scores]
        pivot_pts = detect_pivot_points(composites)
        pivot_count = sum(1 for s in self._scores if s.is_pivot)

        alerts = [
            {
                "step": s.step_index,
                "score": s.composite_score,
                "classification": s.classification.value,
                "topic": s.topic_label,
            }
            for s in self._scores
            if s.alert
        ]

        from adhd_drift.topics import most_visited_topic as mvt

        return SessionReport(
            steps=list(self._scores),
            total_steps=len(self._scores),
            total_pivots=pivot_count,
            peak_drift=round(peak, 4),
            peak_drift_step=peak_idx,
            mean_drift=round(sum(composites) / len(composites), 4),
            final_classification=self._scores[-1].classification,
            drift_velocity_trend=drift_velocity_trend(composites),
            longest_focus_streak=longest_focus_streak(classifications),
            most_visited_topic=mvt(topic_labels),
            topic_sequence=topic_labels,
            pivot_points=pivot_pts,
            alerts=alerts,
        )

    def to_dict(self) -> dict:
        """Serialize the session report for JSON/UI consumption."""
        report = self.report()
        initial_goal = report.topic_sequence[0] if report.topic_sequence else ""
        returned_to_goal = initial_goal in report.topic_sequence[1:] if initial_goal else False
        return {
            "initial_goal": initial_goal,
            "returned_to_goal": returned_to_goal,
            "total_steps": report.total_steps,
            "total_pivots": report.total_pivots,
            "peak_drift": report.peak_drift,
            "peak_drift_step": report.peak_drift_step,
            "mean_drift": report.mean_drift,
            "final_classification": report.final_classification.value,
            "drift_velocity_trend": report.drift_velocity_trend,
            "longest_focus_streak": report.longest_focus_streak,
            "most_visited_topic": report.most_visited_topic,
            "topic_sequence": report.topic_sequence,
            "pivot_points": report.pivot_points,
            "alerts": report.alerts,
            "steps": [
                {
                    "index": s.step_index,
                    "score": s.composite_score,
                    "classification": s.classification.value,
                    "cumulative_drift": s.cumulative_drift,
                    "recovery_score": s.recovery_score,
                    "topic_label": s.topic_label,
                    "is_pivot": s.is_pivot,
                    "alert": s.alert,
                    "suggestions": s.suggestions,
                    "signals": {
                        "semantic_distance": round(s.signals.semantic_distance, 4),
                        "topic_divergence": round(s.signals.topic_divergence, 4),
                        "specificity_shift": round(s.signals.specificity_shift, 4),
                        "velocity": round(s.signals.velocity, 4),
                    },
                }
                for s in report.steps
            ],
        }
