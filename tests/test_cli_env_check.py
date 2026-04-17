"""Tests for cli_env_check commands."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from stashenv.cli_env_check import check_cmd
from stashenv.store import save_profile

PASSWORD = "testpass"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def project_dir(tmp_path):
    return tmp_path


def _write_example(project_dir, keys):
    (project_dir / ".env.example").write_text("\n".join(f"{k}=x" for k in keys))


def _save(project_dir, profile, env_dict):
    text = "\n".join(f"{k}={v}" for k, v in env_dict.items())
    save_profile(project_dir, profile, text, PASSWORD)


def test_check_passes(runner, project_dir):
    _write_example(project_dir, ["KEY"])
    _save(project_dir, "dev", {"KEY": "val"})
    result = runner.invoke(
        check_cmd,
        ["run", "dev", "--project-dir", str(project_dir), "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "OK" in result.output


def test_check_missing_key_exits_1(runner, project_dir):
    _write_example(project_dir, ["KEY", "MISSING"])
    _save(project_dir, "dev", {"KEY": "val"})
    result = runner.invoke(
        check_cmd,
        ["run", "dev", "--project-dir", str(project_dir), "--password", PASSWORD],
    )
    assert result.exit_code == 1
    assert "MISSING" in result.output


def test_check_no_example_file(runner, project_dir):
    _save(project_dir, "dev", {"KEY": "val"})
    result = runner.invoke(
        check_cmd,
        ["run", "dev", "--project-dir", str(project_dir), "--password", PASSWORD],
    )
    assert result.exit_code != 0


def test_check_strict_flag(runner, project_dir):
    _write_example(project_dir, ["KEY"])
    _save(project_dir, "dev", {"KEY": "val", "BONUS": "extra"})
    result = runner.invoke(
        check_cmd,
        [
            "run", "dev",
            "--project-dir", str(project_dir),
            "--password", PASSWORD,
            "--strict",
        ],
    )
    assert result.exit_code == 1
    assert "EXTRA" in result.output
    assert "BONUS" in result.output
