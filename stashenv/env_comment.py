"""Add, update, and remove inline comments on env profile keys."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from stashenv.store import _profile_path, load_profile, save_profile


class CommentError(Exception):
    pass


def _comments_path(project_dir: Path, profile: str) -> Path:
    return _profile_path(project_dir, profile).with_suffix(".comments.json")


def _load_comments(project_dir: Path, profile: str) -> dict[str, str]:
    import json

    path = _comments_path(project_dir, profile)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_comments(project_dir: Path, profile: str, comments: dict[str, str]) -> None:
    import json

    path = _comments_path(project_dir, profile)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(comments, indent=2))


def set_comment(project_dir: Path, profile: str, key: str, comment: str, password: str) -> None:
    """Attach a comment to *key* in *profile*. Raises CommentError if key not found."""
    env = load_profile(project_dir, profile, password)
    if key not in env:
        raise CommentError(f"Key '{key}' not found in profile '{profile}'.")
    comments = _load_comments(project_dir, profile)
    comments[key] = comment
    _save_comments(project_dir, profile, comments)


def get_comment(project_dir: Path, profile: str, key: str) -> Optional[str]:
    """Return the comment for *key*, or None if none is set."""
    return _load_comments(project_dir, profile).get(key)


def remove_comment(project_dir: Path, profile: str, key: str) -> None:
    """Remove the comment for *key* (no-op if none exists)."""
    comments = _load_comments(project_dir, profile)
    comments.pop(key, None)
    _save_comments(project_dir, profile, comments)


def list_comments(project_dir: Path, profile: str) -> dict[str, str]:
    """Return all key -> comment mappings for *profile*."""
    return dict(_load_comments(project_dir, profile))


def format_comments(comments: dict[str, str]) -> str:
    """Render comments as a human-readable string."""
    if not comments:
        return "(no comments)"
    lines = [f"  {k}: {v}" for k, v in sorted(comments.items())]
    return "\n".join(lines)
