"""Tests for stashenv.cli_ttl."""

from __future__ import annotations

import time
from pathlib import Path

import pytest
from click.testing import CliRunner

from stashenv.cli_ttl import ttl_cmd
from stashenv.store import save_profile

PASSWORD = "secret"
ENV_CONTENT = b"KEY=value\n"


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(project_dir: Path, profile: str) -> None:
    save_profile(project_dir, profile, ENV_CONTENT, PASSWORD)


def test_set_cmd_success(runner: CliRunner, project_dir: Path) -> None:
    _save(project_dir, "dev")
    result = runner.invoke(ttl_cmd, ["set", "dev", "3600", "--project", str(project_dir)])
    assert result.exit_code == 0
    assert "3600s" in result.output


def test_set_cmd_nonexistent_profile(runner: CliRunner, project_dir: Path) -> None:
    result = runner.invoke(ttl_cmd, ["set", "ghost", "60", "--project", str(project_dir)])
    assert result.exit_code == 1
    assert "ghost" in result.output


def test_set_cmd_zero_seconds(runner: CliRunner, project_dir: Path) -> None:
    _save(project_dir, "dev")
    result = runner.invoke(ttl_cmd, ["set", "dev", "0", "--project", str(project_dir)])
    assert result.exit_code == 1


def test_status_cmd_no_ttl(runner: CliRunner, project_dir: Path) -> None:
    _save(project_dir, "dev")
    result = runner.invoke(ttl_cmd, ["status", "dev", "--project", str(project_dir)])
    assert result.exit_code == 0
    assert "No TTL" in result.output


def test_status_cmd_with_ttl(runner: CliRunner, project_dir: Path) -> None:
    _save(project_dir, "dev")
    runner.invoke(ttl_cmd, ["set", "dev", "3600", "--project", str(project_dir)])
    result = runner.invoke(ttl_cmd, ["status", "dev", "--project", str(project_dir)])
    assert result.exit_code == 0
    assert "remaining" in result.output


def test_clear_cmd(runner: CliRunner, project_dir: Path) -> None:
    _save(project_dir, "dev")
    runner.invoke(ttl_cmd, ["set", "dev", "3600", "--project", str(project_dir)])
    result = runner.invoke(ttl_cmd, ["clear", "dev", "--project", str(project_dir)])
    assert result.exit_code == 0
    assert "cleared" in result.output


def test_list_expired_cmd_empty(runner: CliRunner, project_dir: Path) -> None:
    _save(project_dir, "dev")
    result = runner.invoke(ttl_cmd, ["list-expired", "--project", str(project_dir)])
    assert result.exit_code == 0
    assert "No expired" in result.output
