import pytest
from pathlib import Path
from stashenv.store import save_profile
from stashenv.validate import validate_profile, format_validation

PASSWORD = "secret"


@pytest.fixture
def project_dir(tmp_path: Path) -> str:
    return str(tmp_path)


def _save(project_dir, profile, env):
    save_profile(project_dir, profile, env, PASSWORD)


def test_validate_clean_profile(project_dir):
    _save(project_dir, "prod", {"PORT": "8080", "API_KEY": "A" * 32})
    schema = {
        "PORT": {"type": "int", "required": True},
        "API_KEY": {"required": True, "pattern": r"[A-Za-z0-9]{32}"},
    }
    result = validate_profile(project_dir, "prod", PASSWORD, schema)
    assert result.ok
    assert "all checks passed" in format_validation(result)


def test_validate_missing_required_key(project_dir):
    _save(project_dir, "prod", {"PORT": "8080"})
    schema = {"API_KEY": {"required": True}}
    result = validate_profile(project_dir, "prod", PASSWORD, schema)
    assert not result.ok
    assert any(i.rule == "required" for i in result.issues)


def test_validate_wrong_type(project_dir):
    _save(project_dir, "dev", {"PORT": "not_a_number"})
    schema = {"PORT": {"type": "int"}}
    result = validate_profile(project_dir, "dev", PASSWORD, schema)
    assert not result.ok
    assert result.issues[0].rule == "type"


def test_validate_pattern_mismatch(project_dir):
    _save(project_dir, "dev", {"TOKEN": "short"})
    schema = {"TOKEN": {"pattern": r"[A-Z]{10}"}}
    result = validate_profile(project_dir, "dev", PASSWORD, schema)
    assert not result.ok
    assert result.issues[0].rule == "pattern"


def test_validate_optional_missing_key_is_ok(project_dir):
    _save(project_dir, "dev", {"PORT": "3000"})
    schema = {"OPTIONAL_KEY": {"type": "str"}}
    result = validate_profile(project_dir, "dev", PASSWORD, schema)
    assert result.ok


def test_validate_bool_type(project_dir):
    _save(project_dir, "dev", {"DEBUG": "true"})
    schema = {"DEBUG": {"type": "bool"}}
    result = validate_profile(project_dir, "dev", PASSWORD, schema)
    assert result.ok


def test_validate_bool_type_invalid(project_dir):
    _save(project_dir, "dev", {"DEBUG": "maybe"})
    schema = {"DEBUG": {"type": "bool"}}
    result = validate_profile(project_dir, "dev", PASSWORD, schema)
    assert not result.ok


def test_format_validation_shows_issues(project_dir):
    _save(project_dir, "dev", {})
    schema = {"KEY": {"required": True}}
    result = validate_profile(project_dir, "dev", PASSWORD, schema)
    output = format_validation(result)
    assert "1 issue" in output
    assert "required" in output
