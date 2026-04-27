"""Schema validation for .env profiles — enforce required keys, types, and patterns."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from stashenv.store import load_profile, list_profiles


@dataclass
class SchemaViolation:
    key: str
    rule: str
    message: str


@dataclass
class SchemaResult:
    profile: str
    violations: list[SchemaViolation] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.violations) == 0


def _load_schema(schema_path: Path) -> dict[str, Any]:
    """Load a JSON schema file describing expected env keys."""
    import json
    with schema_path.open() as fh:
        return json.load(fh)


def validate_against_schema(
    project_dir: Path,
    profile: str,
    password: str,
    schema_path: Path,
) -> SchemaResult:
    """Validate a profile against a JSON schema.

    Schema format::

        {
          "required": ["KEY_A", "KEY_B"],
          "types": {"PORT": "int", "DEBUG": "bool"},
          "patterns": {"EMAIL": "^[^@]+@[^@]+$"}
        }
    """
    env = load_profile(project_dir, profile, password)
    schema = _load_schema(schema_path)
    result = SchemaResult(profile=profile)

    for key in schema.get("required", []):
        if key not in env:
            result.violations.append(
                SchemaViolation(key=key, rule="required", message=f"Missing required key '{key}'")
            )

    for key, expected_type in schema.get("types", {}).items():
        if key not in env:
            continue
        value = env[key]
        if expected_type == "int":
            if not re.fullmatch(r"-?\d+", value):
                result.violations.append(
                    SchemaViolation(key=key, rule="type", message=f"'{key}' must be an integer, got '{value}'")
                )
        elif expected_type == "bool":
            if value.lower() not in ("true", "false", "1", "0"):
                result.violations.append(
                    SchemaViolation(key=key, rule="type", message=f"'{key}' must be a boolean, got '{value}'")
                )
        elif expected_type == "url":
            if not re.match(r"https?://", value):
                result.violations.append(
                    SchemaViolation(key=key, rule="type", message=f"'{key}' must be a URL, got '{value}'")
                )

    for key, pattern in schema.get("patterns", {}).items():
        if key not in env:
            continue
        if not re.fullmatch(pattern, env[key]):
            result.violations.append(
                SchemaViolation(key=key, rule="pattern", message=f"'{key}' does not match pattern '{pattern}'")
            )

    return result


def validate_all_against_schema(
    project_dir: Path,
    password: str,
    schema_path: Path,
) -> list[SchemaResult]:
    """Validate every profile in a project against the given schema."""
    results = []
    for profile in list_profiles(project_dir):
        results.append(validate_against_schema(project_dir, profile, password, schema_path))
    return results


def format_schema_result(result: SchemaResult) -> str:
    if result.ok:
        return f"[OK] {result.profile}: all schema rules passed."
    lines = [f"[FAIL] {result.profile}: {len(result.violations)} violation(s)"]
    for v in result.violations:
        lines.append(f"  [{v.rule}] {v.message}")
    return "\n".join(lines)
