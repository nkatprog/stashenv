"""Count and summarize keys across profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from stashenv.store import list_profiles, load_profile


@dataclass
class ProfileCount:
    profile: str
    total: int
    empty: int
    non_empty: int


@dataclass
class CountSummary:
    project_dir: Path
    profiles: list[ProfileCount] = field(default_factory=list)

    @property
    def total_profiles(self) -> int:
        return len(self.profiles)

    @property
    def grand_total_keys(self) -> int:
        return sum(p.total for p in self.profiles)


def count_profile(project_dir: Path, profile: str, password: str) -> ProfileCount:
    """Return key counts for a single profile."""
    env_text = load_profile(project_dir, profile, password)
    total = 0
    empty = 0
    for line in env_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        total += 1
        _, _, value = line.partition("=")
        if not value.strip():
            empty += 1
    return ProfileCount(
        profile=profile,
        total=total,
        empty=empty,
        non_empty=total - empty,
    )


def count_all_profiles(
    project_dir: Path, password: str, profile_filter: Optional[str] = None
) -> CountSummary:
    """Count keys across all (or filtered) profiles in a project."""
    names = list_profiles(project_dir)
    if profile_filter:
        names = [n for n in names if profile_filter.lower() in n.lower()]
    summary = CountSummary(project_dir=project_dir)
    for name in sorted(names):
        try:
            pc = count_profile(project_dir, name, password)
            summary.profiles.append(pc)
        except Exception:
            pass
    return summary


def format_count(summary: CountSummary) -> str:
    """Render a CountSummary as a human-readable table."""
    if not summary.profiles:
        return "No profiles found."
    lines = [f"{'Profile':<30} {'Total':>6} {'Non-empty':>10} {'Empty':>6}"]
    lines.append("-" * 56)
    for pc in summary.profiles:
        lines.append(
            f"{pc.profile:<30} {pc.total:>6} {pc.non_empty:>10} {pc.empty:>6}"
        )
    lines.append("-" * 56)
    lines.append(
        f"{'TOTAL':<30} {summary.grand_total_keys:>6} "
        f"{sum(p.non_empty for p in summary.profiles):>10} "
        f"{sum(p.empty for p in summary.profiles):>6}"
    )
    return "\n".join(lines)
