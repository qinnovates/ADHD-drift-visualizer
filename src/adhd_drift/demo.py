"""Demo session showing ADHD-style conversation drift.

A realistic chat session where someone starts working on auth, pivots to a
CSS bug, remembers a meeting, circles back, then drifts into architecture.
"""

from adhd_drift.types import ChatMessage

SAMPLE_SESSION = [
    ChatMessage(
        index=0,
        text="Let's fix the auth token refresh. The JWT expires after 15 minutes and users get logged out mid-session.",
        role="user",
    ),
    ChatMessage(
        index=1,
        text="I'll look at the token refresh middleware. The interceptor should catch 401 responses and retry with a fresh token.",
        role="assistant",
    ),
    ChatMessage(
        index=2,
        text="Actually wait, before that — there's a CSS bug on the settings page. The sidebar overlaps the main content on mobile. Can you check that real quick?",
        role="user",
    ),
    ChatMessage(
        index=3,
        text="The sidebar uses position: fixed but doesn't account for the mobile viewport. We need a media query breakpoint at 768px.",
        role="assistant",
    ),
    ChatMessage(
        index=4,
        text="Oh right I have a meeting in 10 minutes about the Q3 roadmap. What were the key features we said we'd ship?",
        role="user",
    ),
    ChatMessage(
        index=5,
        text="Based on the last planning session: auth improvements, dashboard redesign, and the export feature. Auth was priority 1.",
        role="assistant",
    ),
    ChatMessage(
        index=6,
        text="Ok good. Back to the auth thing — actually, should we switch from JWT to session tokens? I read that JWTs are overkill for our use case.",
        role="user",
    ),
    ChatMessage(
        index=7,
        text="That's a bigger architectural decision. JWTs work fine for your scale. The immediate fix is the refresh interceptor — we can evaluate session tokens later.",
        role="assistant",
    ),
    ChatMessage(
        index=8,
        text="You know what, the whole auth layer feels wrong. We're using three different middleware packages. Can we consolidate?",
        role="user",
    ),
    ChatMessage(
        index=9,
        text="That's scope creep from the original ask (token refresh). I'd suggest: fix the refresh bug now, file a ticket for auth consolidation, and tackle it in a dedicated sprint.",
        role="assistant",
    ),
    ChatMessage(
        index=10,
        text="Fair. Let's do the refresh fix. Also can you remind me — did we ever fix that database migration that was failing on staging?",
        role="user",
    ),
    ChatMessage(
        index=11,
        text="I don't have context on the staging migration. That might be a separate issue to investigate. Want to focus on the auth refresh first?",
        role="assistant",
    ),
    ChatMessage(
        index=12,
        text="Yeah let's do it. Show me the interceptor code.",
        role="user",
    ),
]


def run_demo():
    """Run the demo session and print results."""
    from adhd_drift.engine import DriftEngine

    engine = DriftEngine()
    for msg in SAMPLE_SESSION:
        score = engine.add_message(msg)
        pivot_marker = " ** PIVOT **" if score.is_pivot else ""
        print(
            f"  [{score.step_index:2d}] {score.classification.value:18s} "
            f"score={score.composite_score:.3f}  "
            f"topic='{score.topic_label}'{pivot_marker}"
        )

    report = engine.report()
    print("\n--- Session Summary ---")
    print(f"  Total messages:       {report.total_steps}")
    print(f"  Total pivots:         {report.total_pivots}")
    print(f"  Peak drift:           {report.peak_drift:.3f} (step {report.peak_drift_step})")
    print(f"  Mean drift:           {report.mean_drift:.3f}")
    print(f"  Longest focus streak: {report.longest_focus_streak}")
    print(f"  Most visited topic:   {report.most_visited_topic}")
    print(f"  Trend:                {report.drift_velocity_trend}")
    print(f"  Final state:          {report.final_classification.value}")


if __name__ == "__main__":
    run_demo()
