"""Tests for stashenv.cli_env_access."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from stashenv.cli_env_access import access_cmd
from stashenv.env_access import get_permissions, set_access


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_grant_cmd_success(runner: CliRunner, project_dir: Path) -> None:
    result = runner.invoke(
        access_cmd,
        ["grant", "production", "alice", "read", "--project-dir", str(project_dir)],
    )
    assert result.exit_code == 0
    assert "Granted" in result.output
    assert get_permissions(project_dir, "production", "alice") == ["read"]


def test_grant_invalid_permission(runner: CliRunner, project_dir: Path) -> None:
    result = runner.invoke(
        access_cmd,
        ["grant", "production", "alice", "execute", "--project-dir", str(project_dir)],
    )
    assert result.exit_code != 0
    assert "Unknown permissions" in result.output


def test_revoke_cmd_success(runner: CliRunner, project_dir: Path) -> None:
    set_access(project_dir, "production", "alice", ["read"])
    result = runner.invoke(
        access_cmd,
        ["revoke", "production", "alice", "--project-dir", str(project_dir)],
    )
    assert result.exit_code == 0
    assert get_permissions(project_dir, "production", "alice") == []


def test_show_cmd_lists_rules(runner: CliRunner, project_dir: Path) -> None:
    set_access(project_dir, "dev", "bob", ["read", "write"])
    result = runner.invoke(
        access_cmd, ["show", "--project-dir", str(project_dir)]
    )
    assert result.exit_code == 0
    assert "dev" in result.output
    assert "bob" in result.output


def test_show_cmd_empty(runner: CliRunner, project_dir: Path) -> None:
    result = runner.invoke(
        access_cmd, ["show", "--project-dir", str(project_dir)]
    )
    assert result.exit_code == 0
    assert "No access rules" in result.output


def test_check_cmd_passes(runner: CliRunner, project_dir: Path) -> None:
    set_access(project_dir, "dev", "carol", ["read"])
    result = runner.invoke(
        access_cmd,
        ["check", "dev", "carol", "read", "--project-dir", str(project_dir)],
    )
    assert result.exit_code == 0


def test_check_cmd_denied(runner: CliRunner, project_dir: Path) -> None:
    set_access(project_dir, "dev", "carol", ["read"])
    result = runner.invoke(
        access_cmd,
        ["check", "dev", "carol", "write", "--project-dir", str(project_dir)],
    )
    assert result.exit_code != 0
    assert "write" in result.output
