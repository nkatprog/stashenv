"""Sort keys within a profile alphabetically or by custom order."""

from __future__ import annotations

from typing import Optional

from stashenv.store import load_profile, save_profile


class SortError(Exception):
    pass


def sort_profile(
    project_dir: str,
    profile: str,
    password: str,
    *,
    reverse: bool = False,
    group_prefixes: bool = False,
) -> dict[str, str]:
    """Load a profile, sort its keys, and save it back.

    Args:
        project_dir: Path to the project directory.
        profile: Name of the profile to sort.
        password: Encryption password.
        reverse: If True, sort in descending order.
        group_prefixes: If True, keys sharing a common prefix (e.g. DB_)
                        are grouped together before overall sorting.

    Returns:
        The sorted key-value dict that was saved.
    """
    data = load_profile(project_dir, profile, password)

    if group_prefixes:
        sorted_data = _sort_grouped(data, reverse=reverse)
    else:
        sorted_data = dict(sorted(data.items(), key=lambda kv: kv[0], reverse=reverse))

    save_profile(project_dir, profile, password, sorted_data)
    return sorted_data


def _sort_grouped(data: dict[str, str], *, reverse: bool) -> dict[str, str]:
    """Sort keys, keeping keys with the same prefix (before first '_') together."""
    from collections import defaultdict

    groups: dict[str, list[str]] = defaultdict(list)
    for key in data:
        prefix = key.split("_")[0] if "_" in key else key
        groups[prefix].append(key)

    sorted_group_keys = sorted(groups.keys(), reverse=reverse)
    result: dict[str, str] = {}
    for group_key in sorted_group_keys:
        for key in sorted(groups[group_key], reverse=reverse):
            result[key] = data[key]
    return result


def preview_sort(
    project_dir: str,
    profile: str,
    password: str,
    *,
    reverse: bool = False,
    group_prefixes: bool = False,
) -> list[str]:
    """Return the sorted key order without saving."""
    data = load_profile(project_dir, profile, password)
    if group_prefixes:
        sorted_data = _sort_grouped(data, reverse=reverse)
    else:
        sorted_data = dict(sorted(data.items(), key=lambda kv: kv[0], reverse=reverse))
    return list(sorted_data.keys())
