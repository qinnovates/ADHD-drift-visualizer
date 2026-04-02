"""Local dev server for the ADHD Drift Visualizer dashboard."""

from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, send_file, jsonify, request

from adhd_drift.types import ChatMessage, ToleranceProfile
from adhd_drift.engine import DriftEngine

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB upload limit
UI_DIR = Path(__file__).parent

_engine: DriftEngine | None = None


def _get_engine() -> DriftEngine:
    global _engine
    if _engine is None:
        _engine = DriftEngine(profile=ToleranceProfile.standard())
    return _engine


@app.route("/")
def index():
    return send_file(UI_DIR / "dashboard.html")


@app.route("/api/session", methods=["GET"])
def get_session():
    """Return current session state."""
    return jsonify(_get_engine().to_dict())


@app.route("/api/message", methods=["POST"])
def add_message():
    """Add a new message to the session."""
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field"}), 400

    engine = _get_engine()
    msg = ChatMessage(
        index=len(engine.messages),
        text=data["text"],
        role=data.get("role", "user"),
    )
    engine.add_message(msg)
    return jsonify(engine.to_dict())


@app.route("/api/reset", methods=["POST"])
def reset_session():
    """Reset the session."""
    global _engine
    profile_name = request.get_json().get("profile", "standard") if request.is_json else "standard"
    profiles = {
        "strict": ToleranceProfile.strict,
        "standard": ToleranceProfile.standard,
        "creative": ToleranceProfile.creative,
        "freeform": ToleranceProfile.freeform,
    }
    factory = profiles.get(profile_name, ToleranceProfile.standard)
    _engine = DriftEngine(profile=factory())
    return jsonify({"status": "reset", "profile": profile_name})


@app.route("/api/demo", methods=["POST"])
def load_demo():
    """Load the demo session."""
    global _engine
    from adhd_drift.demo import SAMPLE_SESSION

    _engine = DriftEngine(profile=ToleranceProfile.standard())
    for msg in SAMPLE_SESSION:
        _engine.add_message(msg)
    return jsonify(_engine.to_dict())


@app.route("/api/upload", methods=["POST"])
def upload_session():
    """Upload and analyze a chat log file.

    Auto-detects format from file extension:
    - .jsonl → Claude Code session
    - .json  → ChatGPT export
    - .md/.txt/.log → Markdown conversation
    """
    global _engine

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    uploaded = request.files["file"]
    filename = (uploaded.filename or "unknown").lower()
    content = uploaded.read().decode("utf-8")

    messages = _parse_by_extension(filename, content)

    if not messages:
        return jsonify({"error": "Could not parse any messages from file"}), 400

    profile_name = request.form.get("profile", "standard")
    profiles = {
        "strict": ToleranceProfile.strict,
        "standard": ToleranceProfile.standard,
        "creative": ToleranceProfile.creative,
        "freeform": ToleranceProfile.freeform,
    }
    factory = profiles.get(profile_name, ToleranceProfile.standard)
    _engine = DriftEngine(profile=factory())

    for msg in messages:
        _engine.add_message(msg)

    return jsonify(_engine.to_dict())


def _parse_by_extension(filename: str, content: str) -> list[ChatMessage]:
    """Route to the correct parser based on file extension."""
    if filename.endswith(".jsonl"):
        import json
        import tempfile

        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
        tmp.write(content)
        tmp.close()
        try:
            from adhd_drift.parsers.claude import parse_claude_session

            return parse_claude_session(tmp.name)
        finally:
            os.unlink(tmp.name)

    if filename.endswith(".json"):
        import json
        import tempfile

        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        tmp.write(content)
        tmp.close()
        try:
            from adhd_drift.parsers.chatgpt import parse_chatgpt_export

            return parse_chatgpt_export(tmp.name)
        finally:
            os.unlink(tmp.name)

    from adhd_drift.parsers.markdown import parse_markdown_text

    return parse_markdown_text(content)


def main():
    port = int(os.environ.get("PORT", 3457))
    print(f"ADHD Drift Visualizer: http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True)


if __name__ == "__main__":
    main()
