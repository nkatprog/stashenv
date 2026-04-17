"""Tests for stashenv.lint."""
import pytest
from pathlib import Path
from stashenv.store import save_profile
from stashenv.lint import lint_profile, lint_all_profiles, format_lint_result


PASSWORD = "testpass"


@pytest.fixture
def project_dir(tmp_path):
    return str(tmp_path)


def _save(project, profile, content):
    save_profile(project, profile, content, PASSWORD)


def test_lint_clean_profile(project_dir):
    _save(project_dir, "prod", "DATABASE_URL=postgres://localhost/db\nSECRET_KEY=supersecretvalue\n")
    result = lint_profile(project_dir, "prod", PASSWORD)
    assert result.profile == "prod"
    assert result.issues == []
    assert result.ok


def test_lint_empty_value(project_dir):
    _save(project_dir, "dev", "API_KEY=\n")
    result = lint_profile(project_dir, "dev", PASSWORD)
    keys_warned = [i.key for i in result.issues]
    assert "API_KEY" in keys_warned
    messages = [i.message for i in result.issues]
    assert any("empty" in m for m in messages)


def test_lint_lowercase_key(project_dir):
    _save(project_dir, "dev", "myVar=hello\n")
    result = lint_profile(project_dir, "dev", PASSWORD)
    issues = [i for i in result.issues if i.key == "myVar"]
    assert any("uppercase" in i.message for i in issues)


def test_lint_key_with_spaces(project_dir):
    _save(project_dir, "dev", "BAD KEY=value\n")
    result = lint_profile(project_dir, "dev", PASSWORD)
    issues = [i for i in result.issues if i.key == "BAD KEY"]
    assert any(i.severity == "error" for i in issues)
    assert not result.ok


def test_lint_short_secret(project_dir):
    _save(project_dir, "dev", "API_SECRET=abc\n")
    result = lint_profile(project_dir, "dev", PASSWORD)
    issues = [i for i in result.issues if i.key == "API_SECRET"]
    assert any("too short" in i.message for i in issues)


def test_lint_all_profiles(project_dir):
    _save(project_dir, "prod", "CLEAN=value\n")
    _save(project_dir, "dev", "lower=bad\n")
    results = lint_all_profiles(project_dir, PASSWORD)
    assert len(results) == 2
    profiles = {r.profile for r in results}
    assert {"prod", "dev"} == profiles


def test_format_lint_result_ok(project_dir):
    _save(project_dir, "prod", "GOOD=value\n")
    result = lint_profile(project_dir, "prod", PASSWORD)
    output = format_lint_result(result)
    assert "OK" in output


def test_format_lint_result_with_issues(project_dir):
    _save(project_dir, "dev", "bad key=\n")
    result = lint_profile(project_dir, "dev", PASSWORD)
    output = format_lint_result(result)
    assert "ERROR" in output or "WARNING" in output
    assert "dev" in output
