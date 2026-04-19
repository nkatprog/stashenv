"""Validate .env profile values against a schema (type/pattern/required rules)."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Any
from stashenv.store import load_profile


@dataclass
class ValidationIssue:
    key: str
    rule: str
    message: str


@dataclass
class ValidationResult:
    profile: str
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0


SCHEMA_TYPES = {"str", "int", "float", "bool"}


def _check_type(value: str, expected: str) -> bool:
    try:
        if expected == "int":
            int(value)
        elif expected == "float":
            float(value)
        elif expected == "bool":
            if value.lower() not in ("true", "false", "1", "0", "yes", "no"):
                return False
        return True
    except ValueError:
        return False


def validate_profile(
    project_dir: str,
    profile: str,
    password: str,
    schema: dict[str, dict[str, Any]],
) -> ValidationResult:
    """Validate a profile against a schema dict.

    Schema example::

        {
            "PORT": {"type": "int", "required": True},
            "API_KEY": {"required": True, "pattern": r"^[A-Za-z0-9]{32}$"},
        }
    """
    result = ValidationResult(profile=profile)
    env = load_profile(project_dir, profile, password)

    for key, rules in schema.items():
        required = rules.get("required", False)
        if key not in env:
            if required:
                result.issues.append(ValidationIssue(key, "required", f"{key} is required but missing"))
            continue
        value = env[key]
        if "type" in rules:
            expected_type = rules["type"]
            if not _check_type(value, expected_type):
                result.issues.append(ValidationIssue(key, "type", f"{key}={value!r} is not a valid {expected_type}"))
        if "pattern" in rules:
            if not re.fullmatch(rules["pattern"], value):
                result.issues.append(ValidationIssue(key, "pattern", f"{key}={value!r} does not match pattern {rules['pattern']!r}"))

    return result


def format_validation(result: ValidationResult) -> str:
    if result.ok:
        return f"Profile '{result.profile}': all checks passed."
    lines = [f"Profile '{result.profile}': {len(result.issues)} issue(s)"]
    for issue in result.issues:
        lines.append(f"  [{issue.rule}] {issue.message}")
    return "\n".join(lines)
