"""Compute statistics about profiles and their key-value contents."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from stashenv.store import list_profiles, load_profile
from stashenv.export import env_to_dict


@dataclass
class ProfileStats:
    profile: str
    total_keys: int
    empty_values: int
    unique_values: int
    duplicate_values: int
    longest_key: Optional[str]
    longest_value_key: Optional[str]
    avg_value_length: float


@dataclass
class ProjectStats:
    project_dir: str
    total_profiles: int
    total_keys: int
    profiles: List[ProfileStats] = field(default_factory=list)


def _stats_for_env(profile: str, env_text: str) -> ProfileStats:
    data = env_to_dict(env_text)
    if not data:
        return ProfileStats(
            profile=profile,
            total_keys=0,
            empty_values=0,
            unique_values=0,
            duplicate_values=0,
            longest_key=None,
            longest_value_key=None,
            avg_value_length=0.0,
        )

    values = list(data.values())
    value_counts: Dict[str, int] = {}
    for v in values:
        value_counts[v] = value_counts.get(v, 0) + 1

    unique_values = sum(1 for c in value_counts.values() if c == 1)
    duplicate_values = len(values) - unique_values
    empty_values = sum(1 for v in values if v == "")
    longest_key = max(data.keys(), key=len)
    longest_value_key = max(data.keys(), key=lambda k: len(data[k]))
    avg_value_length = sum(len(v) for v in values) / len(values)

    return ProfileStats(
        profile=profile,
        total_keys=len(data),
        empty_values=empty_values,
        unique_values=unique_values,
        duplicate_values=duplicate_values,
        longest_key=longest_key,
        longest_value_key=longest_value_key,
        avg_value_length=round(avg_value_length, 2),
    )


def profile_stats(project_dir: str, profile: str, password: str) -> ProfileStats:
    env_text = load_profile(project_dir, profile, password)
    return _stats_for_env(profile, env_text)


def project_stats(project_dir: str, password: str) -> ProjectStats:
    profiles = list_profiles(project_dir)
    all_stats: List[ProfileStats] = []
    for p in profiles:
        try:
            env_text = load_profile(project_dir, p, password)
            all_stats.append(_stats_for_env(p, env_text))
        except Exception:
            pass
    total_keys = sum(s.total_keys for s in all_stats)
    return ProjectStats(
        project_dir=str(project_dir),
        total_profiles=len(all_stats),
        total_keys=total_keys,
        profiles=all_stats,
    )


def format_profile_stats(s: ProfileStats) -> str:
    lines = [
        f"Profile : {s.profile}",
        f"  Keys            : {s.total_keys}",
        f"  Empty values    : {s.empty_values}",
        f"  Unique values   : {s.unique_values}",
        f"  Duplicate values: {s.duplicate_values}",
        f"  Avg value len   : {s.avg_value_length}",
        f"  Longest key     : {s.longest_key or '-'}",
        f"  Longest val key : {s.longest_value_key or '-'}",
    ]
    return "\n".join(lines)
