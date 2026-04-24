"""Bulk set/unset environment variables across a profile."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from stashenv.store import load_profile, save_profile


class EnvSetError(Exception):
    pass


def set_vars(project_dir: Path, profile: str, password: str, updates: Dict[str, str]) -> Dict[str, str]:
    """Set multiple key=value pairs in a profile. Returns the updated env dict."""
    env = load_profile(project_dir, profile, password)
    env.update(updates)
    save_profile(project_dir, profile, password, env)
    return env


def unset_vars(project_dir: Path, profile: str, password: str, keys: List[str]) -> Dict[str, str]:
    """Remove multiple keys from a profile. Missing keys are silently skipped."""
    env = load_profile(project_dir, profile, password)
    for key in keys:
        env.pop(key, None)
    save_profile(project_dir, profile, password, env)
    return env


def set_from_file(
    project_dir: Path,
    profile: str,
    password: str,
    env_file: Path,
    overwrite: bool = True,
) -> Dict[str, str]:
    """Bulk-import key=value pairs from a plain .env file into a profile.

    Lines starting with '#' and blank lines are ignored.
    If *overwrite* is False, existing keys are kept.
    """
    if not env_file.exists():
        raise EnvSetError(f"File not found: {env_file}")

    incoming: Dict[str, str] = {}
    for raw in env_file.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise EnvSetError(f"Invalid line (no '='): {line!r}")
        key, _, value = line.partition("=")
        incoming[key.strip()] = value.strip()

    env = load_profile(project_dir, profile, password)
    if overwrite:
        env.update(incoming)
    else:
        for k, v in incoming.items():
            env.setdefault(k, v)
    save_profile(project_dir, profile, password, env)
    return env
