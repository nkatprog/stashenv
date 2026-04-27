"""Tests for stashenv.env_trim."""

from __future__ import annotations

import pytest

from stashenv.store import save_profile, load_profile
from stashenv.env_trim import trim_profile, format_trim_result, TrimError


PASSWORD = "secret"


@pytest.fixture()
def project_dir(tmp_path):
    return str(tmp_path)


def _save(project_dir, profile, env):
    save_profile(project_dir, profile, env, PASSWORD)


def test_trim_clean_profile_returns_clean_result(project_dir):
    _save(project_dir, "dev", {"KEY": "value", "OTHER": "ok"})
    result = trim_profile(project_dir, "dev", PASSWORD)
    assert result.clean
    assert result.total == 0


def test_trim_values_strips_whitespace(project_dir):
    _save(project_dir, "dev", {"KEY": "  hello  ", "B": "world"})
    result = trim_profile(project_dir, "dev", PASSWORD)
    assert not result.clean
    assert "KEY" in result.trimmed_values
    env = load_profile(project_dir, "dev", PASSWORD)
    assert env["KEY"] == "hello"
    assert env["B"] == "world"


def test_trim_keys_strips_whitespace(project_dir):
    _save(project_dir, "dev", {" SPACED ": "value"})
    result = trim_profile(project_dir, "dev", PASSWORD)
    assert " SPACED " in result.trimmed_keys
    env = load_profile(project_dir, "dev", PASSWORD)
    assert "SPACED" in env
    assert " SPACED " not in env


def test_trim_dry_run_does_not_persist(project_dir):
    _save(project_dir, "dev", {"KEY": "  dirty  "})
    result = trim_profile(project_dir, "dev", PASSWORD, dry_run=True)
    assert not result.clean
    env = load_profile(project_dir, "dev", PASSWORD)
    assert env["KEY"] == "  dirty  "


def test_trim_only_values_leaves_keys_unchanged(project_dir):
    _save(project_dir, "dev", {" K ": "  v  "})
    result = trim_profile(project_dir, "dev", PASSWORD, trim_keys=False)
    assert result.trimmed_keys == []
    assert result.trimmed_values != []
    env = load_profile(project_dir, "dev", PASSWORD)
    assert " K " in env
    assert env[" K "] == "v"


def test_trim_only_keys_leaves_values_unchanged(project_dir):
    _save(project_dir, "dev", {" K ": "  v  "})
    result = trim_profile(project_dir, "dev", PASSWORD, trim_values=False)
    assert result.trimmed_values == []
    env = load_profile(project_dir, "dev", PASSWORD)
    assert "K" in env
    assert env["K"] == "  v  "


def test_format_trim_result_clean(project_dir):
    _save(project_dir, "dev", {"A": "b"})
    result = trim_profile(project_dir, "dev", PASSWORD)
    out = format_trim_result(result)
    assert "clean" in out


def test_format_trim_result_dirty(project_dir):
    _save(project_dir, "dev", {"KEY": "  value  "})
    result = trim_profile(project_dir, "dev", PASSWORD, dry_run=True)
    out = format_trim_result(result)
    assert "Values trimmed" in out
    assert "KEY" in out
