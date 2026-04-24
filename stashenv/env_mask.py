"""Mask sensitive values in a profile for safe display."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from stashenv.store import load_profile

# Keys whose values should always be fully masked
_ALWAYS_MASK = {
    "PASSWORD", "PASSWD", "SECRET", "TOKEN", "API_KEY", "APIKEY",
    "PRIVATE_KEY", "AUTH", "CREDENTIAL", "CREDENTIALS", "ACCESS_KEY",
    "ACCESS_TOKEN", "REFRESH_TOKEN", "CLIENT_SECRET",
}

MASK_CHAR = "*"
DEFAULT_REVEAL_CHARS = 4


@dataclass
class MaskResult:
    profile: str
    project_dir: str
    masked: dict[str, str]
    revealed_keys: list[str] = field(default_factory=list)


def _should_mask(key: str, extra_patterns: Optional[list[str]] = None) -> bool:
    upper = key.upper()
    if upper in _ALWAYS_MASK:
        return True
    for pattern in (_ALWAYS_MASK if extra_patterns is None else extra_patterns):
        if pattern.upper() in upper:
            return True
    return False


def _mask_value(value: str, reveal_chars: int = 0) -> str:
    if not value:
        return value
    if reveal_chars <= 0 or reveal_chars >= len(value):
        return MASK_CHAR * max(len(value), 6)
    visible = value[:reveal_chars]
    return visible + MASK_CHAR * (len(value) - reveal_chars)


def mask_profile(
    profile: str,
    password: str,
    project_dir: str,
    reveal_chars: int = DEFAULT_REVEAL_CHARS,
    extra_patterns: Optional[list[str]] = None,
    show_all: bool = False,
) -> MaskResult:
    """Load a profile and return a masked view of its values."""
    env = load_profile(profile, password, project_dir)
    masked: dict[str, str] = {}
    revealed_keys: list[str] = []

    for key, value in env.items():
        if show_all or not _should_mask(key, extra_patterns):
            masked[key] = value
            revealed_keys.append(key)
        else:
            masked[key] = _mask_value(value, reveal_chars)

    return MaskResult(
        profile=profile,
        project_dir=project_dir,
        masked=masked,
        revealed_keys=revealed_keys,
    )


def format_masked(result: MaskResult) -> str:
    """Format a MaskResult for terminal display."""
    lines = [f"Profile: {result.profile}  ({result.project_dir})", ""]
    for key, value in result.masked.items():
        lines.append(f"  {key}={value}")
    return "\n".join(lines)
