"""Tests for stashenv.env_freeze."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from stashenv.crypto import encrypt
from stashenv.store import _profile_path, save_profile
from stashenv.env_freeze import (
    FreezeError,
    assert_not_frozen,
    freeze_profile,
    is_frozen,
    list_frozen,
    unfreeze_profile,
)
from stashenv.cli_freeze import freeze_cmd


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(project_dir: Path, profile: str, password: str = "pw") -> None:
    save_profile(project_dir, profile, b"KEY=val\n", password)


# --- unit tests ---

def test_freeze_profile_marks_as_frozen(project_dir: Path) -> None:
    _save(project_dir, "dev")
    freeze_profile(project_dir, "dev")
    assert is_frozen(project_dir, "dev") is True


def test_freeze_nonexistent_profile_raises(project_dir: Path) -> None:
    with pytest.raises(FreezeError, match="does not exist"):
        freeze_profile(project_dir, "ghost")


def test_unfreeze_clears_frozen(project_dir: Path) -> None:
    _save(project_dir, "dev")
    freeze_profile(project_dir, "dev")
    unfreeze_profile(project_dir, "dev")
    assert is_frozen(project_dir, "dev") is False


def test_unfreeze_noop_when_not_frozen(project_dir: Path) -> None:
    _save(project_dir, "dev")
    unfreeze_profile(project_dir, "dev")  # should not raise
    assert is_frozen(project_dir, "dev") is False


def test_list_frozen_returns_all_frozen(project_dir: Path) -> None:
    _save(project_dir, "dev")
    _save(project_dir, "prod")
    _save(project_dir, "staging")
    freeze_profile(project_dir, "dev")
    freeze_profile(project_dir, "prod")
    assert sorted(list_frozen(project_dir)) == ["dev", "prod"]


def test_list_frozen_empty_when_none(project_dir: Path) -> None:
    assert list_frozen(project_dir) == []


def test_assert_not_frozen_raises_when_frozen(project_dir: Path) -> None:
    _save(project_dir, "prod")
    freeze_profile(project_dir, "prod")
    with pytest.raises(FreezeError, match="frozen"):
        assert_not_frozen(project_dir, "prod")


def test_assert_not_frozen_passes_when_not_frozen(project_dir: Path) -> None:
    _save(project_dir, "dev")
    assert_not_frozen(project_dir, "dev")  # no exception


# --- CLI tests ---

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_cli_freeze_set_and_status(runner: CliRunner, project_dir: Path) -> None:
    _save(project_dir, "dev")
    result = runner.invoke(freeze_cmd, ["set", "dev", "--project", str(project_dir)])
    assert result.exit_code == 0
    assert "frozen" in result.output

    result = runner.invoke(freeze_cmd, ["status", "dev", "--project", str(project_dir)])
    assert "frozen" in result.output


def test_cli_freeze_list(runner: CliRunner, project_dir: Path) -> None:
    _save(project_dir, "dev")
    _save(project_dir, "prod")
    runner.invoke(freeze_cmd, ["set", "dev", "--project", str(project_dir)])
    runner.invoke(freeze_cmd, ["set", "prod", "--project", str(project_dir)])
    result = runner.invoke(freeze_cmd, ["list", "--project", str(project_dir)])
    assert "dev" in result.output
    assert "prod" in result.output


def test_cli_unset_cmd(runner: CliRunner, project_dir: Path) -> None:
    _save(project_dir, "dev")
    runner.invoke(freeze_cmd, ["set", "dev", "--project", str(project_dir)])
    result = runner.invoke(freeze_cmd, ["unset", "dev", "--project", str(project_dir)])
    assert result.exit_code == 0
    assert is_frozen(project_dir, "dev") is False
