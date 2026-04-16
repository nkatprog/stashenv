"""Tests for export/import CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from stashenv.cli_export import export_cmd, import_cmd
from stashenv.store import save_profile


PASSWORD = "clipass"
ENV_CONTENT = "API_KEY=secret\nDEBUG=true\n"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def project_dir(tmp_path):
    return str(tmp_path / "proj")


def test_export_creates_file(runner, project_dir, tmp_path):
    save_profile(project_dir, "prod", PASSWORD, ENV_CONTENT)
    out = str(tmp_path / "out.env")
    result = runner.invoke(export_cmd, ["prod", out, "--password", PASSWORD, "--project", project_dir])
    assert result.exit_code == 0
    assert Path(out).read_text() == ENV_CONTENT
    assert "Exported" in result.output


def test_export_nonexistent_profile(runner, project_dir, tmp_path):
    out = str(tmp_path / "out.env")
    result = runner.invoke(export_cmd, ["ghost", out, "--password", PASSWORD, "--project", project_dir])
    assert result.exit_code != 0


def test_import_then_export_roundtrip(runner, project_dir, tmp_path):
    src = tmp_path / "source.env"
    src.write_text(ENV_CONTENT)
    result = runner.invoke(import_cmd, ["dev", str(src), "--password", PASSWORD, "--project", project_dir])
    assert result.exit_code == 0
    assert "Imported" in result.output

    out = str(tmp_path / "result.env")
    result2 = runner.invoke(export_cmd, ["dev", out, "--password", PASSWORD, "--project", project_dir])
    assert result2.exit_code == 0
    assert Path(out).read_text() == ENV_CONTENT


def test_import_missing_file(runner, project_dir):
    result = runner.invoke(import_cmd, ["dev", "/no/such/file.env", "--password", PASSWORD, "--project", project_dir])
    assert result.exit_code != 0
