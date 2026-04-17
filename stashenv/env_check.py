"""Validate that a loaded profile matches expected keys from a .env.example file."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from stashenv.store import load_profile
from stashenv.export import env_to_dict


@dataclass
class CheckResult:
    profile: str
    missing: list[str] = field(default_factory=list)
    extra: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing and not self.extra


def load_example(example_path: Path) -> set[str]:
    """Return the set of keys defined in a .env.example file."""
    if not example_path.exists():
        raise FileNotFoundError(f"Example file not found: {example_path}")
    text = example_path.read_text()
    return set(env_to_dict(text).keys())


def check_profile(
    project_dir: Path,
    profile: str,
    password: str,
    example_path: Optional[Path] = None,
    strict: bool = False,
) -> CheckResult:
    """Compare a stored profile against a .env.example.

    Args:
        project_dir: Root directory of the project.
        profile: Profile name to check.
        password: Decryption password.
        example_path: Path to .env.example; defaults to project_dir/.env.example.
        strict: If True, extra keys in profile (not in example) are also reported.
    """
    if example_path is None:
        example_path = project_dir / ".env.example"

    expected_keys = load_example(example_path)
    env_text = load_profile(project_dir, profile, password)
    actual_keys = set(env_to_dict(env_text).keys())

    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys) if strict else []
    return CheckResult(profile=profile, missing=missing, extra=extra)


def format_check(result: CheckResult) -> str:
    lines = [f"Profile '{result.profile}': {'OK' if result.ok else 'ISSUES FOUND'}"]
    for k in result.missing:
        lines.append(f"  MISSING : {k}")
    for k in result.extra:
        lines.append(f"  EXTRA   : {k}")
    return "\n".join(lines)
