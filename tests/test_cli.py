import os
import pytest
from click.testing import CliRunner
from stashenv.cli import cli


PASSWORD = "testpassword"
ENV_CONTENT = b"API_KEY=abc123\nDEBUG=true\n"


@pytest.fixture
def runner(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    env_file = tmp_path / ".env"
    env_file.write_bytes(ENV_CONTENT)
    return CliRunner(), tmp_path


def test_save_and_list(runner):
    r, tmp_path = runner
    result = r.invoke(cli, ["save", "dev"], input=f"{PASSWORD}\n{PASSWORD}\n")
    assert result.exit_code == 0, result.output
    assert "Profile 'dev' saved." in result.output

    result = r.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "dev" in result.output


def test_save_load_roundtrip(runner):
    r, tmp_path = runner
    r.invoke(cli, ["save", "staging"], input=f"{PASSWORD}\n{PASSWORD}\n")

    out_file = str(tmp_path / ".env.out")
    result = r.invoke(
        cli, ["load", "staging", "--env-file", out_file],
        input=f"{PASSWORD}\n{PASSWORD}\n"
    )
    assert result.exit_code == 0, result.output
    assert os.path.exists(out_file)
    assert open(out_file, "rb").read() == ENV_CONTENT


def test_load_wrong_password(runner):
    r, _ = runner
    r.invoke(cli, ["save", "prod"], input=f"{PASSWORD}\n{PASSWORD}\n")
    result = r.invoke(cli, ["load", "prod"], input="wrongpassword\nwrongpassword\n")
    assert result.exit_code != 0
    assert "Error" in result.output


def test_load_nonexistent_profile(runner):
    r, _ = runner
    result = r.invoke(cli, ["load", "ghost"], input=f"{PASSWORD}\n{PASSWORD}\n")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_delete_profile(runner):
    r, _ = runner
    r.invoke(cli, ["save", "temp"], input=f"{PASSWORD}\n{PASSWORD}\n")
    result = r.invoke(cli, ["delete", "temp"], input="y\n")
    assert result.exit_code == 0
    assert "deleted" in result.output

    result = r.invoke(cli, ["list"])
    assert "temp" not in result.output


def test_save_missing_env_file(runner):
    r, tmp_path = runner
    result = r.invoke(
        cli, ["save", "dev", "--env-file", "nonexistent.env"],
        input=f"{PASSWORD}\n{PASSWORD}\n"
    )
    assert result.exit_code != 0
    assert "not found" in result.output
