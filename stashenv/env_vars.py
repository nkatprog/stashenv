"""Set, get, unset, and list individual key-value pairs within a stored profile."""

from __future__ import annotations

from typing import Optional

from stashenv.store import load_profile, save_profile, list_profiles


class KeyNotFoundError(KeyError):
    """Raised when a requested key does not exist in the profile."""


def set_var(project_dir: str, profile: str, password: str, key: str, value: str) -> None:
    """Set (or overwrite) a single variable in an existing profile."""
    env = load_profile(project_dir, profile, password)
    env[key] = value
    save_profile(project_dir, profile, password, env)


def get_var(project_dir: str, profile: str, password: str, key: str) -> str:
    """Return the value of a single variable from a profile.

    Raises KeyNotFoundError if the key is absent.
    """
    env = load_profile(project_dir, profile, password)
    if key not in env:
        raise KeyNotFoundError(f"Key '{key}' not found in profile '{profile}'.")
    return env[key]


def unset_var(project_dir: str, profile: str, password: str, key: str) -> None:
    """Remove a single variable from a profile.

    Raises KeyNotFoundError if the key does not exist.
    """
    env = load_profile(project_dir, profile, password)
    if key not in env:
        raise KeyNotFoundError(f"Key '{key}' not found in profile '{profile}'.")
    del env[key]
    save_profile(project_dir, profile, password, env)


def list_vars(project_dir: str, profile: str, password: str) -> dict[str, str]:
    """Return all key-value pairs in a profile as a plain dict."""
    return load_profile(project_dir, profile, password)


def rename_var(
    project_dir: str,
    profile: str,
    password: str,
    old_key: str,
    new_key: str,
    overwrite: bool = False,
) -> None:
    """Rename a key inside a profile, preserving its value.

    Raises KeyNotFoundError if old_key is absent.
    Raises KeyError if new_key already exists and overwrite is False.
    """
    env = load_profile(project_dir, profile, password)
    if old_key not in env:
        raise KeyNotFoundError(f"Key '{old_key}' not found in profile '{profile}'.")
    if new_key in env and not overwrite:
        raise KeyError(
            f"Key '{new_key}' already exists in profile '{profile}'. "
            "Use overwrite=True to replace it."
        )
    env[new_key] = env.pop(old_key)
    save_profile(project_dir, profile, password, env)
