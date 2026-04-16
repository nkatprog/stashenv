"""Tests for CLI rotate commands."""

import pytest
from click.testing import CliRunner
from stashenv.store import save_profile, load_profile
from stashenv.cli_rotate import rotate_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def project_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHENV_DIR", str(tmp_path))
    return tmp_path


def test_rotate_single_profile(runner, project_dir):
    save_profile("myapp", "dev", "KEY=val\n", "oldpass")
    result = runner.invoke(
        rotate_cmd,
        ["myapp", "dev", "--old-password", "oldpass", "--new-password", "newpass"],
    )
    assert result.exit_code == 0
    assert "Rotated password for profile 'dev'" in result.output
    assert load_profile("myapp", "dev", "newpass") == "KEY=val\n"


def test_rotate_all_profiles(runner, project_dir):
    for name in ("dev", "prod"):
        save_profile("myapp", name, f"ENV={name}\n", "oldpass")
    result = runner.invoke(
        rotate_cmd,
        ["myapp", "--old-password", "oldpass", "--new-password", "newpass"],
    )
    assert result.exit_code == 0
    assert "2 profile(s)" in result.output


def test_rotate_wrong_old_password(runner, project_dir):
    save_profile("myapp", "dev", "KEY=val\n", "correct")
    result = runner.invoke(
        rotate_cmd,
        ["myapp", "dev", "--old-password", "wrong", "--new-password", "newpass"],
    )
    assert result.exit_code != 0


def test_rotate_empty_project(runner, project_dir):
    result = runner.invoke(
        rotate_cmd,
        ["emptyapp", "--old-password", "pass", "--new-password", "newpass"],
    )
    assert result.exit_code == 0
    assert "No profiles found" in result.output
