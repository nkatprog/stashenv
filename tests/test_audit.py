"""Tests for stashenv.audit module."""

import pytest
from pathlib import Path
from stashenv.audit import log_event, read_log, format_log


@pytest.fixture
def project_dir(tmp_path):
    return str(tmp_path)


def test_log_event_creates_file(project_dir):
    log_event(project_dir, "save", "production")
    log_path = Path(project_dir) / ".stashenv" / "audit.log"
    assert log_path.exists()


def test_read_log_empty_when_no_file(project_dir):
    events = read_log(project_dir)
    assert events == []


def test_log_and_read_single_event(project_dir):
    log_event(project_dir, "save", "staging", user="alice")
    events = read_log(project_dir)
    assert len(events) == 1
    assert events[0]["action"] == "save"
    assert events[0]["profile"] == "staging"
    assert events[0]["user"] == "alice"
    assert "timestamp" in events[0]


def test_log_multiple_events(project_dir):
    log_event(project_dir, "save", "dev", user="bob")
    log_event(project_dir, "load", "dev", user="bob")
    log_event(project_dir, "delete", "dev", user="bob")
    events = read_log(project_dir)
    assert len(events) == 3
    assert [e["action"] for e in events] == ["save", "load", "delete"]


def test_log_event_with_extra(project_dir):
    log_event(project_dir, "copy", "prod", user="carol", extra={"dest": "prod-backup"})
    events = read_log(project_dir)
    assert events[0]["dest"] == "prod-backup"


def test_format_log_empty():
    result = format_log([])
    assert result == "No audit events found."


def test_format_log_contains_fields(project_dir):
    log_event(project_dir, "load", "production", user="dave")
    events = read_log(project_dir)
    output = format_log(events)
    assert "dave" in output
    assert "load" in output
    assert "production" in output


def test_format_log_multiple_lines(project_dir):
    log_event(project_dir, "save", "a", user="u1")
    log_event(project_dir, "load", "b", user="u2")
    events = read_log(project_dir)
    output = format_log(events)
    assert len(output.splitlines()) == 2
