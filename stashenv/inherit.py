"""Profile inheritance: apply a base profile's values as defaults for a child profile."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from stashenv.store import load_profile, save_profile, list_profiles


def _merge_base_into_child(
    base: dict[str, str],
    child: dict[str, str],
    override: bool = False,
) -> dict[str, str]:
    """Return a new dict with base values as defaults for child.

    If override=True, base values overwrite child values.
    Otherwise, child values take precedence (default behaviour).
    """
    if override:
        merged = dict(child)
        merged.update(base)
    else:
        merged = dict(base)
        merged.update(child)
    return merged


def inherit_profile(
    project_dir: Path,
    base_profile: str,
    child_profile: str,
    password: str,
    base_password: Optional[str] = None,
    override: bool = False,
) -> dict[str, str]:
    """Load base and child profiles, merge, save back to child, and return merged dict.

    Args:
        project_dir: Root directory of the project.
        base_profile: Name of the profile to use as base/defaults.
        child_profile: Name of the profile to receive merged values.
        password: Password for the child profile (used to load and re-save it).
        base_password: Password for the base profile. Defaults to `password`.
        override: If True, base values overwrite child values.

    Returns:
        The merged environment dict that was saved into the child profile.

    Raises:
        FileNotFoundError: If either profile does not exist.
        ValueError: If base_profile and child_profile are the same.
    """
    if base_profile == child_profile:
        raise ValueError("base_profile and child_profile must be different.")

    base_password = base_password or password

    base_env = load_profile(project_dir, base_profile, base_password)
    child_env = load_profile(project_dir, child_profile, password)

    merged = _merge_base_into_child(base_env, child_env, override=override)
    save_profile(project_dir, child_profile, merged, password)
    return merged


def apply_base_to_all(
    project_dir: Path,
    base_profile: str,
    password: str,
    override: bool = False,
) -> dict[str, dict[str, str]]:
    """Apply base profile defaults to every other profile in the project.

    Returns a mapping of profile_name -> merged env dict.
    """
    results: dict[str, dict[str, str]] = {}
    for name in list_profiles(project_dir):
        if name == base_profile:
            continue
        results[name] = inherit_profile(
            project_dir,
            base_profile=base_profile,
            child_profile=name,
            password=password,
            override=override,
        )
    return results
