"""Rename keys within a stored profile without changing values."""

from __future__ import annotations

from stashenv.store import load_profile, save_profile


class KeyRenameError(Exception):
    pass


def rename_key(
    project_dir: str,
    profile: str,
    old_key: str,
    new_key: str,
    password: str,
) -> None:
    """Rename *old_key* to *new_key* inside *profile*.

    Raises KeyRenameError if *old_key* does not exist or *new_key* already exists.
    """
    env = load_profile(project_dir, profile, password)

    if old_key not in env:
        raise KeyRenameError(f"Key '{old_key}' not found in profile '{profile}'.")
    if new_key in env:
        raise KeyRenameError(
            f"Key '{new_key}' already exists in profile '{profile}'. "
            "Remove it first or choose a different name."
        )

    # Preserve insertion order: rebuild dict with renamed key in-place.
    renamed: dict[str, str] = {}
    for k, v in env.items():
        renamed[new_key if k == old_key else k] = v

    save_profile(project_dir, profile, renamed, password)


def bulk_rename_keys(
    project_dir: str,
    profile: str,
    mapping: dict[str, str],
    password: str,
) -> None:
    """Rename multiple keys at once using *mapping* {old_key: new_key}.

    All renames are validated before any change is applied.
    """
    env = load_profile(project_dir, profile, password)

    for old_key, new_key in mapping.items():
        if old_key not in env:
            raise KeyRenameError(f"Key '{old_key}' not found in profile '{profile}'.")

    # Check for collisions after all renames are applied.
    result = dict(env)
    for old_key, new_key in mapping.items():
        if new_key in result and new_key not in mapping:
            raise KeyRenameError(
                f"Key '{new_key}' already exists and is not being renamed away."
            )
        result[new_key] = result.pop(old_key)

    save_profile(project_dir, profile, result, password)
