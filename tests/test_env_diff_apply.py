"""Tests for stashenv.env_diff_apply."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from stashenv.store import save_profile, load_profile
from stashenv.env_diff_apply import apply_diff, _parse, _unparse
from stashenv.cli_env_diff_apply import apply_diff_cmd


PASSWORD = "secret"


@pytest.fixture()
def project_dir(tmp_path):
    return str(tmp_path)


def _save(project: str, name: str, env: str) -> None:
    save_profile(project, name, env, PASSWORD)


# --- unit tests for helpers ---

def test_parse_basic():
    text = "FOO=bar\nBAZ=qux\n"
    assert _parse(text) == {"FOO": "bar", "BAZ": "qux"}


def test_parse_skips_comments_and_blanks():
    text = "# comment\n\nFOO=1\n"
    assert _parse(text) == {"FOO": "1"}


def test_unparse_roundtrip():
    d = {"B": "2", "A": "1"}
    assert _parse(_unparse(d)) == d


# --- integration tests ---

def test_apply_adds_missing_keys(project_dir):
    _save(project_dir, "base", "FOO=1\nBAR=2\n")
    _save(project_dir, "target", "FOO=1\n")

    result = apply_diff(project_dir, "base", project_dir, "target", PASSWORD)

    assert "BAR" in result.applied
    assert "FOO" in result.skipped
    assert result.conflicts == []

    loaded = load_profile(project_dir, "target", PASSWORD)
    assert "BAR=2" in loaded


def test_apply_conflict_ours_keeps_target(project_dir):
    _save(project_dir, "base", "FOO=from_base\n")
    _save(project_dir, "target", "FOO=from_target\n")

    result = apply_diff(project_dir, "base", project_dir, "target", PASSWORD, strategy="ours")

    assert "FOO" in result.conflicts
    loaded = load_profile(project_dir, "target", PASSWORD)
    assert "FOO=from_target" in loaded


def test_apply_conflict_theirs_overwrites(project_dir):
    _save(project_dir, "base", "FOO=from_base\n")
    _save(project_dir, "target", "FOO=from_target\n")

    result = apply_diff(project_dir, "base", project_dir, "target", PASSWORD, strategy="theirs")

    assert result.conflicts == []
    assert "FOO" in result.applied
    loaded = load_profile(project_dir, "target", PASSWORD)
    assert "FOO=from_base" in loaded


def test_apply_dry_run_does_not_save(project_dir):
    _save(project_dir, "base", "FOO=1\nNEW=99\n")
    _save(project_dir, "target", "FOO=1\n")

    apply_diff(project_dir, "base", project_dir, "target", PASSWORD, dry_run=True)

    loaded = load_profile(project_dir, "target", PASSWORD)
    assert "NEW" not in loaded


def test_apply_invalid_strategy_raises(project_dir):
    _save(project_dir, "base", "FOO=1\n")
    _save(project_dir, "target", "FOO=1\n")
    with pytest.raises(ValueError, match="Unknown strategy"):
        apply_diff(project_dir, "base", project_dir, "target", PASSWORD, strategy="invalid")


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_apply_success(runner, project_dir):
    _save(project_dir, "base", "FOO=1\nBAR=2\n")
    _save(project_dir, "target", "FOO=1\n")

    result = runner.invoke(
        apply_diff_cmd,
        ["run", "base", "target",
         "--base-project", project_dir,
         "--target-project", project_dir,
         "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "BAR" in result.output


def test_cli_apply_nonexistent_profile(runner, project_dir):
    result = runner.invoke(
        apply_diff_cmd,
        ["run", "ghost", "target",
         "--base-project", project_dir,
         "--target-project", project_dir,
         "--password", PASSWORD],
    )
    assert result.exit_code != 0
