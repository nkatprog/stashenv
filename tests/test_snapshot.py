"""Tests for stashenv.snapshot."""

import pytest
from pathlib import Path

from stashenv.snapshot import create_snapshot, delete_snapshot, list_snapshots, restore_snapshot
from stashenv.store import save_profile, load_profile

PASSWORD = "s3cret"


@pytest.fixture
def project_dir(tmp_path):
    return tmp_path


def _save(project_dir, name, text):
    save_profile(project_dir, name, text, PASSWORD)


def test_create_snapshot_and_list(project_dir):
    _save(project_dir, "dev", "KEY=dev_val")
    _save(project_dir, "prod", "KEY=prod_val")
    sid = create_snapshot(project_dir, PASSWORD, label="snap1")
    assert sid == "snap1"
    assert "snap1" in list_snapshots(project_dir)


def test_list_snapshots_empty(project_dir):
    assert list_snapshots(project_dir) == []


def test_create_snapshot_duplicate_label_raises(project_dir):
    _save(project_dir, "dev", "KEY=val")
    create_snapshot(project_dir, PASSWORD, label="dup")
    with pytest.raises(FileExistsError):
        create_snapshot(project_dir, PASSWORD, label="dup")


def test_restore_snapshot(project_dir):
    _save(project_dir, "dev", "ORIGINAL=yes")
    create_snapshot(project_dir, PASSWORD, label="before")

    # Overwrite the profile
    _save(project_dir, "dev", "ORIGINAL=no")
    assert load_profile(project_dir, "dev", PASSWORD) == "ORIGINAL=no"

    restored = restore_snapshot(project_dir, "before", PASSWORD)
    assert "dev" in restored
    assert load_profile(project_dir, "dev", PASSWORD) == "ORIGINAL=yes"


def test_restore_nonexistent_snapshot_raises(project_dir):
    with pytest.raises(FileNotFoundError):
        restore_snapshot(project_dir, "ghost", PASSWORD)


def test_delete_snapshot(project_dir):
    _save(project_dir, "dev", "K=V")
    create_snapshot(project_dir, PASSWORD, label="to_delete")
    delete_snapshot(project_dir, "to_delete")
    assert "to_delete" not in list_snapshots(project_dir)


def test_delete_nonexistent_snapshot_raises(project_dir):
    with pytest.raises(FileNotFoundError):
        delete_snapshot(project_dir, "missing")
