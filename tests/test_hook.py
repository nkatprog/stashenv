"""Tests for stashenv.hook."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from stashenv.hook import (
    set_hook,
    remove_hook,
    list_hooks,
    run_hook,
    _hooks_path,
)


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_set_hook_creates_file(project_dir: Path) -> None:
    set_hook(project_dir, "dev", "post_load", "echo loaded")
    assert _hooks_path(project_dir).exists()


def test_set_and_list_hook(project_dir: Path) -> None:
    set_hook(project_dir, "dev", "pre_save", "make lint")
    hooks = list_hooks(project_dir, "dev")
    assert hooks == {"pre_save": "make lint"}


def test_set_multiple_events(project_dir: Path) -> None:
    set_hook(project_dir, "prod", "pre_load", "echo before")
    set_hook(project_dir, "prod", "post_load", "echo after")
    hooks = list_hooks(project_dir, "prod")
    assert len(hooks) == 2
    assert hooks["pre_load"] == "echo before"
    assert hooks["post_load"] == "echo after"


def test_list_hooks_empty_when_none(project_dir: Path) -> None:
    assert list_hooks(project_dir, "missing") == {}


def test_remove_hook(project_dir: Path) -> None:
    set_hook(project_dir, "dev", "post_save", "git add .env")
    remove_hook(project_dir, "dev", "post_save")
    assert list_hooks(project_dir, "dev") == {}


def test_remove_hook_cleans_empty_profile(project_dir: Path) -> None:
    set_hook(project_dir, "dev", "pre_load", "true")
    remove_hook(project_dir, "dev", "pre_load")
    raw = json.loads(_hooks_path(project_dir).read_text())
    assert "dev" not in raw


def test_remove_nonexistent_hook_is_noop(project_dir: Path) -> None:
    remove_hook(project_dir, "dev", "pre_load")  # should not raise


def test_run_hook_executes_command(project_dir: Path) -> None:
    marker = project_dir / "ran.txt"
    set_hook(project_dir, "dev", "post_load", f"touch {marker}")
    ran = run_hook(project_dir, "dev", "post_load")
    assert ran is True
    assert marker.exists()


def test_run_hook_returns_false_when_no_hook(project_dir: Path) -> None:
    assert run_hook(project_dir, "dev", "pre_load") is False


def test_run_hook_raises_on_nonzero_exit(project_dir: Path) -> None:
    set_hook(project_dir, "dev", "pre_save", "exit 1")
    with pytest.raises(RuntimeError, match="exited with code 1"):
        run_hook(project_dir, "dev", "pre_save")
