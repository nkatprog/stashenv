"""Tests for stashenv.env_schema."""
import json
from pathlib import Path

import pytest

from stashenv.store import save_profile
from stashenv.env_schema import (
    validate_against_schema,
    validate_all_against_schema,
    format_schema_result,
    SchemaResult,
)

PASSWORD = "secret"


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(project_dir: Path, profile: str, env: dict[str, str]) -> None:
    text = "\n".join(f"{k}={v}" for k, v in env.items())
    save_profile(project_dir, profile, text, PASSWORD)


def _schema(tmp_path: Path, data: dict) -> Path:
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(data))
    return p


def test_validate_all_keys_present(project_dir: Path, tmp_path: Path) -> None:
    _save(project_dir, "prod", {"DATABASE_URL": "postgres://localhost/db", "PORT": "5432"})
    schema = _schema(tmp_path, {"required": ["DATABASE_URL", "PORT"]})
    result = validate_against_schema(project_dir, "prod", PASSWORD, schema)
    assert result.ok
    assert result.violations == []


def test_validate_missing_required_key(project_dir: Path, tmp_path: Path) -> None:
    _save(project_dir, "prod", {"PORT": "5432"})
    schema = _schema(tmp_path, {"required": ["DATABASE_URL", "PORT"]})
    result = validate_against_schema(project_dir, "prod", PASSWORD, schema)
    assert not result.ok
    assert any(v.key == "DATABASE_URL" and v.rule == "required" for v in result.violations)


def test_validate_type_int_valid(project_dir: Path, tmp_path: Path) -> None:
    _save(project_dir, "dev", {"PORT": "8080"})
    schema = _schema(tmp_path, {"types": {"PORT": "int"}})
    result = validate_against_schema(project_dir, "dev", PASSWORD, schema)
    assert result.ok


def test_validate_type_int_invalid(project_dir: Path, tmp_path: Path) -> None:
    _save(project_dir, "dev", {"PORT": "not-a-number"})
    schema = _schema(tmp_path, {"types": {"PORT": "int"}})
    result = validate_against_schema(project_dir, "dev", PASSWORD, schema)
    assert not result.ok
    assert result.violations[0].rule == "type"


def test_validate_type_bool_valid(project_dir: Path, tmp_path: Path) -> None:
    _save(project_dir, "dev", {"DEBUG": "true"})
    schema = _schema(tmp_path, {"types": {"DEBUG": "bool"}})
    result = validate_against_schema(project_dir, "dev", PASSWORD, schema)
    assert result.ok


def test_validate_type_bool_invalid(project_dir: Path, tmp_path: Path) -> None:
    _save(project_dir, "dev", {"DEBUG": "yes"})
    schema = _schema(tmp_path, {"types": {"DEBUG": "bool"}})
    result = validate_against_schema(project_dir, "dev", PASSWORD, schema)
    assert not result.ok


def test_validate_pattern_match(project_dir: Path, tmp_path: Path) -> None:
    _save(project_dir, "dev", {"ADMIN_EMAIL": "admin@example.com"})
    schema = _schema(tmp_path, {"patterns": {"ADMIN_EMAIL": "^[^@]+@[^@]+$"}})
    result = validate_against_schema(project_dir, "dev", PASSWORD, schema)
    assert result.ok


def test_validate_pattern_no_match(project_dir: Path, tmp_path: Path) -> None:
    _save(project_dir, "dev", {"ADMIN_EMAIL": "not-an-email"})
    schema = _schema(tmp_path, {"patterns": {"ADMIN_EMAIL": "^[^@]+@[^@]+$"}})
    result = validate_against_schema(project_dir, "dev", PASSWORD, schema)
    assert not result.ok
    assert result.violations[0].rule == "pattern"


def test_validate_all_profiles(project_dir: Path, tmp_path: Path) -> None:
    _save(project_dir, "dev", {"PORT": "3000"})
    _save(project_dir, "prod", {"PORT": "443"})
    schema = _schema(tmp_path, {"required": ["PORT"]})
    results = validate_all_against_schema(project_dir, PASSWORD, schema)
    assert len(results) == 2
    assert all(r.ok for r in results)


def test_format_schema_result_ok(project_dir: Path, tmp_path: Path) -> None:
    _save(project_dir, "dev", {"PORT": "3000"})
    schema = _schema(tmp_path, {"required": ["PORT"]})
    result = validate_against_schema(project_dir, "dev", PASSWORD, schema)
    output = format_schema_result(result)
    assert "OK" in output
    assert "dev" in output


def test_format_schema_result_fail(project_dir: Path, tmp_path: Path) -> None:
    _save(project_dir, "dev", {})
    schema = _schema(tmp_path, {"required": ["SECRET_KEY"]})
    result = validate_against_schema(project_dir, "dev", PASSWORD, schema)
    output = format_schema_result(result)
    assert "FAIL" in output
    assert "SECRET_KEY" in output
