"""Tests for stashenv.diff module."""

import pytest
from pathlib import Path
from stashenv.store import save_profile
from stashenv.diff import diff_profiles, format_diff

PASSWORD = "testpass"


@pytest.fixture
def project_dir(tmp_path: Path) -> str:
    return str(tmp_path)


def _save(project_dir, name, content):
    save_profile(project_dir, name, content, PASSWORD)


def test_diff_identical_profiles(project_dir):
    content = "FOO=bar\nBAZ=qux\n"
    _save(project_dir, "a", content)
    _save(project_dir, "b", content)
    diffs = diff_profiles(project_dir, "a", "b", PASSWORD)
    assert diffs == []


def test_diff_changed_value(project_dir):
    _save(project_dir, "a", "FOO=bar\n")
    _save(project_dir, "b", "FOO=baz\n")
    diffs = diff_profiles(project_dir, "a", "b", PASSWORD)
    assert len(diffs) == 1
    assert diffs[0] == ("FOO", "bar", "baz")


def test_diff_key_only_in_one(project_dir):
    _save(project_dir, "a", "FOO=bar\nEXTRA=yes\n")
    _save(project_dir, "b", "FOO=bar\n")
    diffs = diff_profiles(project_dir, "a", "b", PASSWORD)
    assert len(diffs) == 1
    assert diffs[0] == ("EXTRA", "yes", None)


def test_diff_multiple_differences(project_dir):
    _save(project_dir, "a", "A=1\nB=2\n")
    _save(project_dir, "b", "A=1\nB=3\nC=4\n")
    diffs = diff_profiles(project_dir, "a", "b", PASSWORD)
    keys = [d[0] for d in diffs]
    assert "B" in keys
    assert "C" in keys
    assert "A" not in keys


def test_format_diff_identical():
    result = format_diff([], "dev", "prod")
    assert result == "Profiles are identical."


def test_format_diff_shows_changes():
    diffs = [("FOO", "bar", "baz"), ("NEW", None, "val"), ("OLD", "x", None)]
    result = format_diff(diffs, "dev", "prod")
    assert "FOO" in result
    assert "->" in result
    assert "+" in result
    assert "-" in result


def test_diff_wrong_password(project_dir):
    _save(project_dir, "a", "FOO=bar\n")
    _save(project_dir, "b", "FOO=baz\n")
    with pytest.raises(Exception):
        diff_profiles(project_dir, "a", "b", "wrongpass")
