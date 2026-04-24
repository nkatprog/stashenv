"""Tests for stashenv.env_rename."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from stashenv.store import save_profile, load_profile
from stashenv.env_rename import rename_key, bulk_rename_keys, KeyRenameError
from stashenv.cli_env_rename import rename_key_cmd


@pytest.fixture()
def project_dir(tmp_path):
    return str(tmp_path)


def _save(project_dir, profile, data, password="secret"):
    save_profile(project_dir, profile, data, password)


# ---------------------------------------------------------------------------
# Unit tests – rename_key
# ---------------------------------------------------------------------------

def test_rename_key_basic(project_dir):
    _save(project_dir, "dev", {"OLD_KEY": "value", "OTHER": "x"})
    rename_key(project_dir, "dev", "OLD_KEY", "NEW_KEY", "secret")
    env = load_profile(project_dir, "dev", "secret")
    assert "NEW_KEY" in env
    assert env["NEW_KEY"] == "value"
    assert "OLD_KEY" not in env
    assert env["OTHER"] == "x"


def test_rename_key_missing_old_raises(project_dir):
    _save(project_dir, "dev", {"A": "1"})
    with pytest.raises(KeyRenameError, match="not found"):
        rename_key(project_dir, "dev", "MISSING", "B", "secret")


def test_rename_key_new_already_exists_raises(project_dir):
    _save(project_dir, "dev", {"A": "1", "B": "2"})
    with pytest.raises(KeyRenameError, match="already exists"):
        rename_key(project_dir, "dev", "A", "B", "secret")


def test_rename_key_preserves_other_keys(project_dir):
    _save(project_dir, "dev", {"X": "10", "Y": "20", "Z": "30"})
    rename_key(project_dir, "dev", "Y", "W", "secret")
    env = load_profile(project_dir, "dev", "secret")
    assert set(env.keys()) == {"X", "W", "Z"}


# ---------------------------------------------------------------------------
# Unit tests – bulk_rename_keys
# ---------------------------------------------------------------------------

def test_bulk_rename_keys(project_dir):
    _save(project_dir, "dev", {"A": "1", "B": "2", "C": "3"})
    bulk_rename_keys(project_dir, "dev", {"A": "AA", "B": "BB"}, "secret")
    env = load_profile(project_dir, "dev", "secret")
    assert env == {"AA": "1", "BB": "2", "C": "3"}


def test_bulk_rename_missing_key_raises(project_dir):
    _save(project_dir, "dev", {"A": "1"})
    with pytest.raises(KeyRenameError, match="not found"):
        bulk_rename_keys(project_dir, "dev", {"NOPE": "X"}, "secret")


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_rename_success(runner, project_dir):
    _save(project_dir, "dev", {"FOO": "bar"})
    result = runner.invoke(
        rename_key_cmd,
        ["run", "dev", "FOO", "BAZ", "--password", "secret", "--project-dir", project_dir],
    )
    assert result.exit_code == 0
    assert "FOO" in result.output
    assert "BAZ" in result.output


def test_cli_rename_missing_key(runner, project_dir):
    _save(project_dir, "dev", {"FOO": "bar"})
    result = runner.invoke(
        rename_key_cmd,
        ["run", "dev", "MISSING", "NEW", "--password", "secret", "--project-dir", project_dir],
    )
    assert result.exit_code != 0
    assert "not found" in result.output
