"""Lint .env profiles for common issues."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from stashenv.store import load_profile, list_profiles
from stashenv.export import env_to_dict


@dataclass
class LintIssue:
    key: str
    message: str
    severity: str = "warning"  # 'warning' | 'error'


@dataclass
class LintResult:
    profile: str
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)


def lint_profile(project: str, profile: str, password: str) -> LintResult:
    """Lint a single profile and return a LintResult."""
    raw = load_profile(project, profile, password)
    env = env_to_dict(raw)
    result = LintResult(profile=profile)

    for key, value in env.items():
        # Check for empty values
        if value == "":
            result.issues.append(LintIssue(key=key, message="Value is empty", severity="warning"))

        # Check for keys with lowercase letters
        if key != key.upper():
            result.issues.append(LintIssue(key=key, message="Key is not uppercase", severity="warning"))

        # Check for keys with spaces
        if " " in key:
            result.issues.append(LintIssue(key=key, message="Key contains spaces", severity="error"))

        # Check for suspiciously short secrets
        lower = key.lower()
        if any(word in lower for word in ("secret", "password", "token", "key")) and 0 < len(value) < 8:
            result.issues.append(LintIssue(key=key, message="Secret value appears too short (< 8 chars)", severity="warning"))

    return result


def lint_all_profiles(project: str, password: str) -> List[LintResult]:
    """Lint all profiles in a project."""
    return [lint_profile(project, p, password) for p in list_profiles(project)]


def format_lint_result(result: LintResult) -> str:
    if not result.issues:
        return f"[{result.profile}] OK"
    lines = [f"[{result.profile}]"]
    for issue in result.issues:
        lines.append(f"  {issue.severity.upper()}: {issue.key} — {issue.message}")
    return "\n".join(lines)
