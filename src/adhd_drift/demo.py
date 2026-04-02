"""Demo session showing non-linear conversation drift.

A realistic chat session where someone starts planning social media
content, pivots through music, concerts, budgeting, and cross-platform
strategy before circling back.
"""

from adhd_drift.types import ChatMessage

SAMPLE_SESSION = [
    ChatMessage(
        index=0,
        text="I need to figure out my TikTok posting schedule. What times get the most engagement for lifestyle content?",
        role="user",
    ),
    ChatMessage(
        index=1,
        text="For lifestyle content, peak engagement is typically 7-9am and 7-11pm. Tuesday and Thursday tend to perform best. Consistency matters more than perfect timing though.",
        role="assistant",
    ),
    ChatMessage(
        index=2,
        text="Ok cool. Also what hashtags are trending right now? I keep hearing that sound from that one reel — you know the one with the remix of that Sabrina Carpenter song?",
        role="user",
    ),
    ChatMessage(
        index=3,
        text="I can help with trending hashtags. For lifestyle content right now: #dayinmylife, #grwm, #aesthetic. As for the Sabrina Carpenter remix, that's been huge on Reels and TikTok this month.",
        role="assistant",
    ),
    ChatMessage(
        index=4,
        text="Omg wait she's touring right? Are there still tickets for the LA show? I saw someone reselling them but they were like $400",
        role="user",
    ),
    ChatMessage(
        index=5,
        text="Her Short n Sweet tour has most major dates sold out. Resale prices for LA are running $350-500 depending on section. StubHub and SeatGeek are the main resale platforms.",
        role="assistant",
    ),
    ChatMessage(
        index=6,
        text="$400 is a lot. I just paid rent and my car insurance went up this month. How much do TikTok creators actually make? Like is the creator fund even worth it?",
        role="user",
    ),
    ChatMessage(
        index=7,
        text="The TikTok Creator Fund pays roughly 2-4 cents per 1,000 views. Most creators say the real money is in brand deals and affiliate links, not the fund itself. You typically need 100k+ followers before brands reach out consistently.",
        role="assistant",
    ),
    ChatMessage(
        index=8,
        text="That makes sense. What about cross-posting to Instagram Reels? Does the algorithm punish you for posting the same content with a TikTok watermark?",
        role="user",
    ),
    ChatMessage(
        index=9,
        text="Yes, Instagram deprioritizes videos with the TikTok watermark. Best practice is to export without watermark using SnapTik or save the original before posting to TikTok. Some creators film once and edit separately for each platform.",
        role="assistant",
    ),
    ChatMessage(
        index=10,
        text="Smart. Ok back to the original question — for my posting schedule, should I batch content on weekends and schedule it out? What tools are good for that?",
        role="user",
    ),
    ChatMessage(
        index=11,
        text="Batching is the move. Later and Buffer both support TikTok scheduling now. Film 5-7 videos on Sunday, schedule for the week. Keeps you consistent without daily pressure.",
        role="assistant",
    ),
    ChatMessage(
        index=12,
        text="Perfect. I'll try batching this Sunday. Oh wait — do you think I should start a separate account for my cooking content or keep everything on one?",
        role="user",
    ),
]


def run_demo():
    """Run the demo session and print results."""
    from adhd_drift.engine import DriftEngine

    engine = DriftEngine()
    for msg in SAMPLE_SESSION:
        score = engine.add_message(msg)
        pivot_marker = " *PIVOT*" if score.is_pivot else ""
        print(
            f"  [{score.step_index:2d}] {score.classification.value:12s} "
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
