import pytest
from click.testing import CliRunner
from pathlib import Path
from stashenv.cli_pin import pin_cmd
from stashenv.store import save_profile


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def project_dir(tmp_path):
    return tmp_path


def _save(project_dir, name, password="pw"):
    save_profile(project_dir, name, {"K": "v"}, password)


def test_set_pin(runner, project_dir):
    _save(project_dir, "dev")
    result = runner.invoke(pin_cmd, ["set", "dev", "--project", str(project_dir)])
    assert result.exit_code == 0
    assert "Pinned 'dev'" in result.output


def test_set_pin_nonexistent(runner, project_dir):
    result = runner.invoke(pin_cmd, ["set", "ghost", "--project", str(project_dir)])
    assert result.exit_code == 1
    assert "does not exist" in result.output


def test_status_shows_pinned(runner, project_dir):
    _save(project_dir, "staging")
    runner.invoke(pin_cmd, ["set", "staging", "--project", str(project_dir)])
    result = runner.invoke(pin_cmd, ["status", "--project", str(project_dir)])
    assert "staging" in result.output


def test_status_no_pin(runner, project_dir):
    result = runner.invoke(pin_cmd, ["status", "--project", str(project_dir)])
    assert "No profile" in result.output


def test_unset_pin(runner, project_dir):
    _save(project_dir, "dev")
    runner.invoke(pin_cmd, ["set", "dev", "--project", str(project_dir)])
    result = runner.invoke(pin_cmd, ["unset", "--project", str(project_dir)])
    assert result.exit_code == 0
    status = runner.invoke(pin_cmd, ["status", "--project", str(project_dir)])
    assert "No profile" in status.output
