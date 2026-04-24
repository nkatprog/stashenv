"""Tests for stashenv.cli_archive."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from stashenv.cli_archive import archive_cmd
from stashenv.store import save_profile


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(project_dir: Path, profile: str, data: dict, password: str = "secret") -> None:
    save_profile(project_dir, profile, data, password)


def test_store_cmd_success(runner: CliRunner, project_dir: Path) -> None:
    _save(project_dir, "dev", {"KEY": "value"})
    result = runner.invoke(
        archive_cmd,
        ["store", "dev", "--password", "secret", "--project", str(project_dir)],
    )
    assert result.exit_code == 0
    assert "archived" in result.output


def test_store_cmd_nonexistent_profile(runner: CliRunner, project_dir: Path) -> None:
    result = runner.invoke(
        archive_cmd,
        ["store", "ghost", "--password", "secret", "--project", str(project_dir)],
    )
    assert result.exit_code == 1


def test_restore_cmd_success(runner: CliRunner, project_dir: Path) -> None:
    _save(project_dir, "dev", {"K": "v"})
    runner.invoke(
        archive_cmd,
        ["store", "dev", "--password", "secret", "--project", str(project_dir)],
    )
    result = runner.invoke(
        archive_cmd,
        ["restore", "dev", "--password", "secret", "--project", str(project_dir)],
    )
    assert result.exit_code == 0
    assert "restored" in result.output


def test_list_cmd_empty(runner: CliRunner, project_dir: Path) -> None:
    result = runner.invoke(
        archive_cmd, ["list", "--project", str(project_dir)]
    )
    assert result.exit_code == 0
    assert "No archived" in result.output


def test_list_cmd_shows_archived(runner: CliRunner, project_dir: Path) -> None:
    _save(project_dir, "staging", {"X": "1"})
    runner.invoke(
        archive_cmd,
        ["store", "staging", "--password", "secret", "--project", str(project_dir)],
    )
    result = runner.invoke(
        archive_cmd, ["list", "--project", str(project_dir)]
    )
    assert result.exit_code == 0
    assert "staging" in result.output
