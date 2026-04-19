"""Tests for stashenv.watch."""
import pytest
from pathlib import Path
from stashenv.watch import watch_env_file
from stashenv.store import load_profile
from stashenv.export import dict_to_env


@pytest.fixture
def project_dir(tmp_path):
    return tmp_path / "project"


def test_watch_detects_change(project_dir, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\nBAZ=qux\n")

    messages = []

    import time

    original_sleep = time.sleep

    call_count = 0

    def fake_sleep(interval):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # Simulate file change by bumping mtime
            env_file.write_text("FOO=changed\n")
            import os
            stat = env_file.stat()
            os.utime(env_file, (stat.st_atime, stat.st_mtime + 1))

    import stashenv.watch as watch_mod
    monkeypatch_sleep = fake_sleep

    original = watch_mod.time.sleep
    watch_mod.time.sleep = fake_sleep
    try:
        watch_env_file(
            env_file=env_file,
            project_dir=project_dir,
            profile="dev",
            password="secret",
            interval=0.01,
            max_iterations=2,
            on_change=messages.append,
        )
    finally:
        watch_mod.time.sleep = original

    assert any("dev" in m for m in messages)
    content = load_profile(project_dir, "dev", "secret")
    assert "FOO=changed" in content


def test_watch_no_change_does_not_save(project_dir, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\n")

    messages = []

    import stashenv.watch as watch_mod
    original = watch_mod.time.sleep
    watch_mod.time.sleep = lambda _: None
    try:
        watch_env_file(
            env_file=env_file,
            project_dir=project_dir,
            profile="dev",
            password="secret",
            interval=0.01,
            max_iterations=3,
            on_change=messages.append,
        )
    finally:
        watch_mod.time.sleep = original

    assert messages == []
