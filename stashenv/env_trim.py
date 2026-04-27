"""Trim whitespace from keys and/or values in a stored profile."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from stashenv.store import load_profile, save_profile


@dataclass
class TrimResult:
    profile: str
    trimmed_keys: list[str] = field(default_factory=list)
    trimmed_values: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.trimmed_keys) + len(self.trimmed_values)

    @property
    def clean(self) -> bool:
        return self.total == 0


class TrimError(Exception):
    pass


def trim_profile(
    project_dir: str,
    profile: str,
    password: str,
    *,
    trim_keys: bool = True,
    trim_values: bool = True,
    dry_run: bool = False,
) -> TrimResult:
    """Strip leading/trailing whitespace from keys and/or values.

    Returns a TrimResult describing what was changed.  When *dry_run* is
    True the profile is not written back to disk.
    """
    env = load_profile(project_dir, profile, password)
    result = TrimResult(profile=profile)

    new_env: dict[str, str] = {}
    for key, value in env.items():
        new_key = key.strip() if trim_keys else key
        new_value = value.strip() if trim_values else value

        if new_key != key:
            result.trimmed_keys.append(key)
        if new_value != value:
            result.trimmed_values.append(new_key)

        if new_key != key and new_key in env and new_key != key:
            raise TrimError(
                f"Trimming key '{key}' would collide with existing key '{new_key}'"
            )

        new_env[new_key] = new_value

    if not dry_run and not result.clean:
        save_profile(project_dir, profile, new_env, password)

    return result


def format_trim_result(result: TrimResult) -> str:
    lines: list[str] = []
    if result.clean:
        lines.append(f"Profile '{result.profile}' is already clean — nothing to trim.")
        return "\n".join(lines)

    if result.trimmed_keys:
        lines.append(f"Keys trimmed ({len(result.trimmed_keys)}):")
        for k in result.trimmed_keys:
            lines.append(f"  {k!r}")
    if result.trimmed_values:
        lines.append(f"Values trimmed ({len(result.trimmed_values)}):")
        for k in result.trimmed_values:
            lines.append(f"  {k}")
    return "\n".join(lines)
