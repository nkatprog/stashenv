"""Format (pretty-print) a stored .env profile in-place or to stdout."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from stashenv.store import load_profile, save_profile, list_profiles


class FormatError(Exception):
    """Raised when formatting fails."""


def _sort_key(line: str) -> tuple[int, str]:
    """Return a sort key that groups blank/comment lines after real keys."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return (1, stripped)
    return (0, stripped.split("=", 1)[0].upper())


def format_env_text(
    text: str,
    *,
    sort_keys: bool = True,
    strip_comments: bool = False,
    strip_blanks: bool = False,
) -> str:
    """Return a formatted version of raw .env text."""
    lines = text.splitlines()
    result = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if strip_blanks:
                continue
            result.append("")
            continue
        if stripped.startswith("#"):
            if strip_comments:
                continue
            result.append(stripped)
            continue
        if "=" not in stripped:
            raise FormatError(f"Invalid line (no '='): {line!r}")
        key, _, value = stripped.partition("=")
        result.append(f"{key.strip()}={value.strip()}")

    if sort_keys:
        # stable-sort: keep comment/blank lines adjacent to their key
        result = sorted(result, key=_sort_key)

    return "\n".join(result)


def format_profile(
    project_dir: Path,
    profile: str,
    password: str,
    *,
    sort_keys: bool = True,
    strip_comments: bool = False,
    strip_blanks: bool = False,
) -> str:
    """Load, format, save, and return the formatted .env text."""
    text = load_profile(project_dir, profile, password)
    formatted = format_env_text(
        text,
        sort_keys=sort_keys,
        strip_comments=strip_comments,
        strip_blanks=strip_blanks,
    )
    save_profile(project_dir, profile, password, formatted)
    return formatted


def format_all_profiles(
    project_dir: Path,
    password: str,
    *,
    sort_keys: bool = True,
    strip_comments: bool = False,
    strip_blanks: bool = False,
) -> dict[str, str]:
    """Format every profile in the project; return {name: formatted_text}."""
    results: dict[str, str] = {}
    for name in list_profiles(project_dir):
        results[name] = format_profile(
            project_dir,
            name,
            password,
            sort_keys=sort_keys,
            strip_comments=strip_comments,
            strip_blanks=strip_blanks,
        )
    return results
