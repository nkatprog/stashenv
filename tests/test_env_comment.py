"""Tests for stashenv.env_comment."""

from pathlib import Path

import pytest

from stashenv.env_comment import (
    CommentError,
    format_comments,
    get_comment,
    list_comments,
    remove_comment,
    set_comment,
)
from stashenv.store import save_profile


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def _save(project_dir: Path, profile: str, data: dict, password: str = "secret") -> None:
    save_profile(project_dir, profile, data, password)


def test_set_and_get_comment(project_dir: Path) -> None:
    _save(project_dir, "dev", {"DB_HOST": "localhost", "PORT": "5432"})
    set_comment(project_dir, "dev", "DB_HOST", "Primary database host", "secret")
    assert get_comment(project_dir, "dev", "DB_HOST") == "Primary database host"


def test_get_comment_none_when_not_set(project_dir: Path) -> None:
    _save(project_dir, "dev", {"API_KEY": "abc"})
    assert get_comment(project_dir, "dev", "API_KEY") is None


def test_set_comment_nonexistent_key_raises(project_dir: Path) -> None:
    _save(project_dir, "dev", {"DB_HOST": "localhost"})
    with pytest.raises(CommentError, match="MISSING_KEY"):
        set_comment(project_dir, "dev", "MISSING_KEY", "oops", "secret")


def test_remove_comment_clears_entry(project_dir: Path) -> None:
    _save(project_dir, "dev", {"PORT": "8080"})
    set_comment(project_dir, "dev", "PORT", "HTTP port", "secret")
    remove_comment(project_dir, "dev", "PORT")
    assert get_comment(project_dir, "dev", "PORT") is None


def test_remove_comment_noop_when_absent(project_dir: Path) -> None:
    _save(project_dir, "dev", {"PORT": "8080"})
    # Should not raise
    remove_comment(project_dir, "dev", "PORT")


def test_list_comments_returns_all(project_dir: Path) -> None:
    _save(project_dir, "dev", {"A": "1", "B": "2", "C": "3"})
    set_comment(project_dir, "dev", "A", "first", "secret")
    set_comment(project_dir, "dev", "C", "third", "secret")
    result = list_comments(project_dir, "dev")
    assert result == {"A": "first", "C": "third"}


def test_list_comments_empty_when_none(project_dir: Path) -> None:
    _save(project_dir, "dev", {"X": "1"})
    assert list_comments(project_dir, "dev") == {}


def test_format_comments_sorted_output(project_dir: Path) -> None:
    _save(project_dir, "dev", {"Z": "1", "A": "2"})
    set_comment(project_dir, "dev", "Z", "last", "secret")
    set_comment(project_dir, "dev", "A", "first", "secret")
    output = format_comments(list_comments(project_dir, "dev"))
    assert output.index("A:") < output.index("Z:")


def test_format_comments_empty_message() -> None:
    assert format_comments({}) == "(no comments)"
