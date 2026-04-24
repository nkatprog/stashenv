"""Merge two named profiles into a new profile, with configurable conflict strategy."""

from __future__ import annotations

from typing import Literal

from stashenv.store import load_profile, save_profile

ConflictStrategy = Literal["base", "override", "error"]


class MergeConflictError(Exception):
    """Raised when two profiles share a key and strategy is 'error'."""


def _merge_dicts(
    base: dict[str, str],
    override: dict[str, str],
    strategy: ConflictStrategy,
) -> dict[str, str]:
    """Merge *override* into *base* according to *strategy*.

    Strategies:
      base     – keep the value from *base* on conflict
      override – keep the value from *override* on conflict
      error    – raise MergeConflictError on any conflicting key
    """
    conflicts = set(base.keys()) & set(override.keys())

    if strategy == "error" and conflicts:
        raise MergeConflictError(
            f"Conflicting keys: {', '.join(sorted(conflicts))}"
        )

    merged: dict[str, str] = dict(base)

    for key, value in override.items():
        if key in conflicts:
            if strategy == "override":
                merged[key] = value
            # strategy == "base": keep existing value — do nothing
        else:
            merged[key] = value

    return merged


def merge_profiles(
    project_dir: str,
    base_profile: str,
    override_profile: str,
    dest_profile: str,
    password: str,
    *,
    strategy: ConflictStrategy = "override",
    dest_project_dir: str | None = None,
    dest_password: str | None = None,
) -> dict[str, str]:
    """Load *base_profile* and *override_profile*, merge them, and save as *dest_profile*.

    Parameters
    ----------
    project_dir:       directory that owns both source profiles
    base_profile:      name of the base profile
    override_profile:  name of the profile whose values win on conflict
                       (when strategy is 'override')
    dest_profile:      name of the resulting merged profile
    password:          decryption password for both source profiles
    strategy:          conflict resolution strategy (default: 'override')
    dest_project_dir:  if given, save the merged profile here instead
    dest_password:     if given, encrypt the merged profile with this password

    Returns the merged key/value mapping.
    """
    base_data = load_profile(project_dir, base_profile, password)
    override_data = load_profile(project_dir, override_profile, password)

    merged = _merge_dicts(base_data, override_data, strategy)

    save_profile(
        dest_project_dir or project_dir,
        dest_profile,
        merged,
        dest_password or password,
    )
    return merged
