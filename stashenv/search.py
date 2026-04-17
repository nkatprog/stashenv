"""Search across profiles for keys or values."""
from __future__ import annotations
from typing import Optional
from stashenv.store import list_profiles, load_profile
from stashenv.export import env_to_dict


def search_profiles(
    project_dir: str,
    password: str,
    query: str,
    search_values: bool = False,
) -> dict[str, list[tuple[str, str]]]:
    """Search all profiles for keys (or values) matching query.

    Returns a dict mapping profile name -> list of (key, value) matches.
    """
    results: dict[str, list[tuple[str, str]]] = {}
    query_lower = query.lower()

    for profile in list_profiles(project_dir):
        try:
            env_text = load_profile(project_dir, profile, password)
        except Exception:
            continue
        pairs = env_to_dict(env_text)
        matches = []
        for key, value in pairs.items():
            if query_lower in key.lower():
                matches.append((key, value))
            elif search_values and query_lower in value.lower():
                matches.append((key, value))
        if matches:
            results[profile] = matches

    return results


def format_search_results(
    results: dict[str, list[tuple[str, str]]],
    reveal_values: bool = False,
) -> str:
    """Format search results for display."""
    if not results:
        return "No matches found."
    lines = []
    for profile, matches in sorted(results.items()):
        lines.append(f"[{profile}]")
        for key, value in matches:
            display = value if reveal_values else "***"
            lines.append(f"  {key}={display}")
    return "\n".join(lines)
