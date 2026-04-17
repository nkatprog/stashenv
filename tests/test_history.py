"""Tests for stashenv.history."""
import pytest
from pathlib import Path
from stashenv.history import record_change, get_history, clear_history, format_history


@pytest.fixture
def project_dir(tmp_path):
    return tmp_path


def test_record_and_get_history(project_dir):
    record_change(project_dir, "prod", "save")
    records = get_history(project_dir)
    assert len(records) == 1
    assert records[0]["profile"] == "prod"
    assert records[0]["action"] == "save"


def test_get_history_empty(project_dir):
    assert get_history(project_dir) == []


def test_filter_by_profile(project_dir):
    record_change(project_dir, "prod", "save")
    record_change(project_dir, "dev", "save")
    record_change(project_dir, "prod", "rotate")
    results = get_history(project_dir, profile="prod")
    assert len(results) == 2
    assert all(r["profile"] == "prod" for r in results)


def test_record_with_note(project_dir):
    record_change(project_dir, "staging", "delete", note="cleanup")
    records = get_history(project_dir)
    assert records[0]["note"] == "cleanup"


def test_clear_all_history(project_dir):
    record_change(project_dir, "prod", "save")
    record_change(project_dir, "dev", "save")
    removed = clear_history(project_dir)
    assert removed == 2
    assert get_history(project_dir) == []


def test_clear_profile_history(project_dir):
    record_change(project_dir, "prod", "save")
    record_change(project_dir, "dev", "save")
    removed = clear_history(project_dir, profile="prod")
    assert removed == 1
    remaining = get_history(project_dir)
    assert len(remaining) == 1
    assert remaining[0]["profile"] == "dev"


def test_format_history_empty():
    assert format_history([]) == "No history found."


def test_format_history_shows_entries(project_dir):
    record_change(project_dir, "prod", "save", note="initial")
    records = get_history(project_dir)
    output = format_history(records)
    assert "prod" in output
    assert "save" in output
    assert "initial" in output
