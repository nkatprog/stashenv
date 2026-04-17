"""Tests for stashenv.env_check."""
import pytest
from pathlib import Path
from stashenv.env_check import check_profile, format_check, CheckResult
from stashenv.store import save_profile

PASSWORD = "testpass"


@pytest.fixture
def project_dir(tmp_path):
    return tmp_path


def _write_example(project_dir: Path, keys: list[str]):
    content = "\n".join(f"{k}=example" for k in keys)
    (project_dir / ".env.example").write_text(content)


def _save(project_dir, profile, env_dict):
    text = "\n".join(f"{k}={v}" for k, v in env_dict.items())
    save_profile(project_dir, profile, text, PASSWORD)


def test_check_ok(project_dir):
    _write_example(project_dir, ["DB_URL", "SECRET"])
    _save(project_dir, "dev", {"DB_URL": "postgres://", "SECRET": "abc"})
    result = check_profile(project_dir, "dev", PASSWORD)
    assert result.ok
    assert result.missing == []
    assert result.extra == []


def test_check_missing_key(project_dir):
    _write_example(project_dir, ["DB_URL", "SECRET", "API_KEY"])
    _save(project_dir, "dev", {"DB_URL": "postgres://", "SECRET": "abc"})
    result = check_profile(project_dir, "dev", PASSWORD)
    assert not result.ok
    assert "API_KEY" in result.missing


def test_check_strict_extra_keys(project_dir):
    _write_example(project_dir, ["DB_URL"])
    _save(project_dir, "dev", {"DB_URL": "postgres://", "EXTRA": "val"})
    result = check_profile(project_dir, "dev", PASSWORD, strict=True)
    assert not result.ok
    assert "EXTRA" in result.extra


def test_check_non_strict_ignores_extra(project_dir):
    _write_example(project_dir, ["DB_URL"])
    _save(project_dir, "dev", {"DB_URL": "postgres://", "EXTRA": "val"})
    result = check_profile(project_dir, "dev", PASSWORD, strict=False)
    assert result.ok


def test_missing_example_raises(project_dir):
    _save(project_dir, "dev", {"DB_URL": "x"})
    with pytest.raises(FileNotFoundError):
        check_profile(project_dir, "dev", PASSWORD)


def test_format_check_ok(project_dir):
    result = CheckResult(profile="dev")
    assert "OK" in format_check(result)


def test_format_check_issues(project_dir):
    result = CheckResult(profile="dev", missing=["API_KEY"], extra=["JUNK"])
    out = format_check(result)
    assert "MISSING" in out
    assert "API_KEY" in out
    assert "EXTRA" in out
    assert "JUNK" in out
