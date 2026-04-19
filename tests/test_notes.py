"""Tests for stashenv.notes and stashenv.cli_notes."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from stashenv.notes import set_note, get_note, clear_note, list_notes
from stashenv.cli_notes import notes_cmd
from stashenv.store import save_profile

PASSWORD = "pw"


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(project_dir: Path, name: str) -> None:
    save_profile(project_dir, name, PASSWORD, {"KEY": "value"})


def test_set_and_get_note(project_dir):
    _save(project_dir, "dev")
    set_note(project_dir, "dev", "Development profile")
    assert get_note(project_dir, "dev") == "Development profile"


def test_get_note_none_when_not_set(project_dir):
    _save(project_dir, "dev")
    assert get_note(project_dir, "dev") is None


def test_set_note_nonexistent_profile_raises(project_dir):
    with pytest.raises(KeyError, match="ghost"):
        set_note(project_dir, "ghost", "some note")


def test_clear_note(project_dir):
    _save(project_dir, "dev")
    set_note(project_dir, "dev", "temp")
    clear_note(project_dir, "dev")
    assert get_note(project_dir, "dev") is None


def test_clear_nonexistent_note_is_noop(project_dir):
    _save(project_dir, "dev")
    clear_note(project_dir, "dev")  # should not raise


def test_list_notes(project_dir):
    _save(project_dir, "dev")
    _save(project_dir, "prod")
    set_note(project_dir, "dev", "note A")
    set_note(project_dir, "prod", "note B")
    notes = list_notes(project_dir)
    assert notes == {"dev": "note A", "prod": "note B"}


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_set_and_get(runner, project_dir):
    _save(project_dir, "dev")
    result = runner.invoke(notes_cmd, ["set", "dev", "hello", "--project", str(project_dir)])
    assert result.exit_code == 0
    result = runner.invoke(notes_cmd, ["get", "dev", "--project", str(project_dir)])
    assert "hello" in result.output


def test_cli_set_nonexistent_profile(runner, project_dir):
    result = runner.invoke(notes_cmd, ["set", "ghost", "note", "--project", str(project_dir)])
    assert result.exit_code != 0


def test_cli_list_empty(runner, project_dir):
    result = runner.invoke(notes_cmd, ["list", "--project", str(project_dir)])
    assert "No notes" in result.output
