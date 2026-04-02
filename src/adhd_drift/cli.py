"""CLI entry point for ADHD Drift Visualizer.

Usage:
    adhd-drift analyze <file>          # Auto-detect format, print JSON report
    adhd-drift analyze <file> --human  # Human-readable summary
    adhd-drift analyze -               # Read from stdin (markdown format)
    adhd-drift serve                   # Launch dashboard server
    adhd-drift demo                    # Run demo session
    adhd-drift history <memory.md>     # Cross-session analysis
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="adhd-drift",
        description="Visualize context-switching patterns in chat sessions",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a chat session file")
    analyze_parser.add_argument("file", help="Path to chat log (- for stdin)")
    analyze_parser.add_argument("--human", action="store_true", help="Human-readable output")
    analyze_parser.add_argument(
        "--profile",
        choices=["strict", "standard", "creative", "freeform"],
        default="standard",
        help="Tolerance profile (default: standard)",
    )

    # serve
    serve_parser = subparsers.add_parser("serve", help="Launch the dashboard server")
    serve_parser.add_argument("--port", type=int, default=3457, help="Port (default: 3457)")

    # demo
    subparsers.add_parser("demo", help="Run demo session with sample conversation")

    # history
    history_parser = subparsers.add_parser("history", help="Cross-session pattern analysis")
    history_parser.add_argument("file", help="Path to MEMORY.md or similar index file")

    args = parser.parse_args()

    if args.command == "analyze":
        _cmd_analyze(args)
    elif args.command == "serve":
        _cmd_serve(args)
    elif args.command == "demo":
        _cmd_demo()
    elif args.command == "history":
        _cmd_history(args)


def _cmd_analyze(args: argparse.Namespace) -> None:
    """Analyze a chat session file."""
    from adhd_drift.types import ToleranceProfile
    from adhd_drift.engine import DriftEngine

    messages = _load_messages(args.file)
    if not messages:
        print("Error: could not parse any messages from input", file=sys.stderr)
        sys.exit(1)

    profiles = {
        "strict": ToleranceProfile.strict,
        "standard": ToleranceProfile.standard,
        "creative": ToleranceProfile.creative,
        "freeform": ToleranceProfile.freeform,
    }
    engine = DriftEngine(profile=profiles[args.profile]())

    for msg in messages:
        engine.add_message(msg)

    if args.human:
        _print_human_report(engine)
    else:
        print(json.dumps(engine.to_dict(), indent=2))


def _load_messages(file_arg: str) -> list:
    """Load messages from a file path or stdin."""
    if file_arg == "-":
        from adhd_drift.parsers.markdown import parse_markdown_text

        content = sys.stdin.read()
        return parse_markdown_text(content)

    path = Path(file_arg)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    suffix = path.suffix.lower()

    if suffix == ".jsonl":
        from adhd_drift.parsers.claude import parse_claude_session

        return parse_claude_session(path)
    elif suffix == ".json":
        from adhd_drift.parsers.chatgpt import parse_chatgpt_export

        return parse_chatgpt_export(path)
    else:
        from adhd_drift.parsers.markdown import parse_markdown_conversation

        return parse_markdown_conversation(path)


def _print_human_report(engine) -> None:
    """Print a human-readable session report to stdout."""
    report = engine.report()

    print("\n  ADHD Drift Visualizer — Session Report")
    print(f"  {'=' * 40}")
    print(f"  Messages:          {report.total_steps}")
    print(f"  Pivots:            {report.total_pivots}")
    print(f"  Peak drift:        {report.peak_drift:.3f} (message {report.peak_drift_step})")
    print(f"  Mean drift:        {report.mean_drift:.3f}")
    print(f"  Focus streak:      {report.longest_focus_streak}")
    print(f"  Most visited:      {report.most_visited_topic}")
    print(f"  Trend:             {report.drift_velocity_trend}")
    print(f"  Final state:       {report.final_classification.value}")
    print()

    if report.topic_sequence:
        seen = []
        for t in report.topic_sequence:
            if not seen or seen[-1] != t:
                seen.append(t)
        print(f"  Topic flow: {' -> '.join(seen)}")
        print()

    for score in report.steps:
        pivot = " *PIVOT*" if score.is_pivot else ""
        print(
            f"  [{score.step_index:2d}] {score.classification.value:12s} "
            f"{score.composite_score:.3f}  {score.topic_label}{pivot}"
        )

    print()


def _cmd_serve(args: argparse.Namespace) -> None:
    """Launch the dashboard server."""
    import os

    os.environ["PORT"] = str(args.port)
    from ui.server import main as serve_main

    serve_main()


def _cmd_demo() -> None:
    """Run the demo session."""
    from adhd_drift.demo import run_demo

    run_demo()


def _cmd_history(args: argparse.Namespace) -> None:
    """Run cross-session pattern analysis."""
    from adhd_drift.history import analyze_memory_file

    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    insight = analyze_memory_file(path)

    print(f"\n  Cross-Session Analysis: {path.name}")
    print(f"  {'=' * 40}")
    print(f"  Total entries:     {insight.total_entries}")
    print(f"  Top topics:        {', '.join(insight.top_topics[:5])}")
    print(f"  Recurring pivots:  {', '.join(insight.recurring_pivots) or 'none'}")

    if insight.topic_clusters:
        print(f"\n  Topic clusters ({len(insight.topic_clusters)}):")
        for cluster in insight.topic_clusters[:5]:
            print(f"    - {cluster[0][:60]}... ({len(cluster)} entries)")

    print()


if __name__ == "__main__":
    main()
