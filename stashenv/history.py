"""Track profile change history per project."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

from stashenv.store import _stash_dir


def _history_path(project_dir: Path) -> Path:
    return _stash_dir(project_dir) / "history.json"


def _load_history(project_dir: Path) -> List[Dict[str, Any]]:
    p = _history_path(project_dir)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_history(project_dir: Path, records: List[Dict[str, Any]]) -> None:
    p = _history_path(project_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(records, indent=2))


def record_change(project_dir: Path, profile: str, action: str, note: str = "") -> None:
    """Append a change record for a profile."""
    records = _load_history(project_dir)
    records.append({
        "profile": profile,
        "action": action,
        "note": note,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    _save_history(project_dir, records)


def get_history(project_dir: Path, profile: str | None = None) -> List[Dict[str, Any]]:
    """Return history records, optionally filtered by profile name."""
    records = _load_history(project_dir)
    if profile:
        records = [r for r in records if r["profile"] == profile]
    return records


def clear_history(project_dir: Path, profile: str | None = None) -> int:
    """Clear history. If profile given, only remove that profile's records."""
    records = _load_history(project_dir)
    if profile:
        kept = [r for r in records if r["profile"] != profile]
        removed = len(records) - len(kept)
        _save_history(project_dir, kept)
        return removed
    _save_history(project_dir, [])
    return len(records)


def format_history(records: List[Dict[str, Any]]) -> str:
    if not records:
        return "No history found."
    lines = []
    for r in records:
        note = f" ({r['note']})" if r.get("note") else ""
        lines.append(f"[{r['timestamp']}] {r['profile']} — {r['action']}{note}")
    return "\n".join(lines)
