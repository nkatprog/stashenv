"""Audit log for profile access and modifications."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _audit_path(project_dir: str) -> Path:
    stash = Path(project_dir) / ".stashenv"
    stash.mkdir(parents=True, exist_ok=True)
    return stash / "audit.log"


def log_event(
    project_dir: str,
    action: str,
    profile: str,
    user: Optional[str] = None,
    extra: Optional[dict] = None,
) -> None:
    """Append a JSON audit event to the project's audit log."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "profile": profile,
        "user": user or os.environ.get("USER", "unknown"),
    }
    if extra:
        event.update(extra)
    with open(_audit_path(project_dir), "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def read_log(project_dir: str) -> list[dict]:
    """Return all audit events for a project as a list of dicts."""
    path = _audit_path(project_dir)
    if not path.exists():
        return []
    events = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def format_log(events: list[dict]) -> str:
    """Format audit events for human-readable display."""
    if not events:
        return "No audit events found."
    lines = []
    for e in events:
        ts = e.get("timestamp", "?")
        action = e.get("action", "?")
        profile = e.get("profile", "?")
        user = e.get("user", "?")
        lines.append(f"[{ts}] {user} {action} '{profile}'")
    return "\n".join(lines)
