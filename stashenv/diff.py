"""Diff two named .env profiles for a project."""

from typing import Dict, List, Tuple
from stashenv.store import load_profile
from stashenv.export import env_to_dict


def _load_as_dict(project_dir: str, profile: str, password: str) -> Dict[str, str]:
    raw = load_profile(project_dir, profile, password)
    return env_to_dict(raw)


def diff_profiles(
    project_dir: str,
    profile_a: str,
    profile_b: str,
    password: str,
) -> List[Tuple[str, str | None, str | None]]:
    """Return list of (key, value_in_a, value_in_b) for keys that differ."""
    dict_a = _load_as_dict(project_dir, profile_a, password)
    dict_b = _load_as_dict(project_dir, profile_b, password)

    all_keys = set(dict_a) | set(dict_b)
    results: List[Tuple[str, str | None, str | None]] = []

    for key in sorted(all_keys):
        val_a = dict_a.get(key)
        val_b = dict_b.get(key)
        if val_a != val_b:
            results.append((key, val_a, val_b))

    return results


def format_diff(
    diffs: List[Tuple[str, str | None, str | None]],
    profile_a: str,
    profile_b: str,
) -> str:
    """Format diff results as a human-readable string."""
    if not diffs:
        return "Profiles are identical."

    lines = [f"Diff: {profile_a} vs {profile_b}", ""]
    for key, val_a, val_b in diffs:
        if val_a is None:
            lines.append(f"  + {key}={val_b}  (only in {profile_b})")
        elif val_b is None:
            lines.append(f"  - {key}={val_a}  (only in {profile_a})")
        else:
            lines.append(f"  ~ {key}: {val_a!r} -> {val_b!r}")
    return "\n".join(lines)
