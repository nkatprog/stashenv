"""Apply a diff patch from one profile onto another, producing a merged result."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from stashenv.store import load_profile, save_profile
from stashenv.diff import diff_profiles, DiffEntry  # type: ignore


@dataclass
class ApplyResult:
    applied: List[str]
    skipped: List[str]
    conflicts: List[str]


def apply_diff(
    base_project: str,
    base_profile: str,
    target_project: str,
    target_profile: str,
    password: str,
    *,
    strategy: str = "ours",
    dry_run: bool = False,
) -> ApplyResult:
    """Apply changes from *base* onto *target*.

    strategy:
      - "ours"   : keep target value on conflict (default)
      - "theirs" : overwrite target value with base value on conflict
    """
    if strategy not in ("ours", "theirs"):
        raise ValueError(f"Unknown strategy {strategy!r}; choose 'ours' or 'theirs'")

    base_env = load_profile(base_project, base_profile, password)
    target_env = load_profile(target_project, target_profile, password)

    base_dict: Dict[str, str] = _parse(base_env)
    target_dict: Dict[str, str] = _parse(target_env)

    applied: List[str] = []
    skipped: List[str] = []
    conflicts: List[str] = []

    for key, value in base_dict.items():
        if key not in target_dict:
            target_dict[key] = value
            applied.append(key)
        elif target_dict[key] == value:
            skipped.append(key)
        else:
            conflicts.append(key)
            if strategy == "theirs":
                target_dict[key] = value
                applied.append(key)
                conflicts.remove(key)

    if not dry_run:
        new_env = _unparse(target_dict)
        save_profile(target_project, target_profile, new_env, password)

    return ApplyResult(applied=applied, skipped=skipped, conflicts=conflicts)


def _parse(env_text: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in env_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, val = line.partition("=")
            result[key.strip()] = val.strip()
    return result


def _unparse(d: Dict[str, str]) -> str:
    return "\n".join(f"{k}={v}" for k, v in sorted(d.items())) + "\n"
