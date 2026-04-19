"""Tests for stashenv.cli_watch."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch
from stashenv.cli_watch import watch_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def project_dir(tmp_path):
    return tmp_path / "project"


def test_start_cmd_calls_watch(runner, tmp_path, project_dir):
    env_file = tmp_path / ".env"
    env_file.write_text("A=1\n")

    with patch("stashenv.cli_watch.watch_env_file") as mock_watch:
        result = runner.invoke(
            watch_cmd,
            [
                "start",
                str(env_file),
                "--project-dir", str(project_dir),
                "--profile", "dev",
                "--password", "secret",
                "--interval", "0.5",
            ],
        )

    assert result.exit_code == 0
    assert "Watching" in result.output
    mock_watch.assert_called_once()
    call_kwargs = mock_watch.call_args
    assert call_kwargs.kwargs["profile"] == "dev"
    assert call_kwargs.kwargs["password"] == "secret"
    assert call_kwargs.kwargs["interval"] == 0.5


def test_start_cmd_missing_env_file(runner, tmp_path, project_dir):
    result = runner.invoke(
        watch_cmd,
        [
            "start",
            str(tmp_path / "nonexistent.env"),
            "--project-dir", str(project_dir),
            "--profile", "dev",
            "--password", "secret",
        ],
    )
    assert result.exit_code != 0
