import pytest
from pathlib import Path
from stashenv.pin import pin_profile, unpin_profile, get_pinned
from stashenv.store import save_profile


@pytest.fixture
def project_dir(tmp_path):
    return tmp_path


def _save(project_dir, name, password="pw", data=None):
    save_profile(project_dir, name, data or {"KEY": "val"}, password)


def test_pin_profile(project_dir):
    _save(project_dir, "dev")
    pin_profile(project_dir, "dev")
    assert get_pinned(project_dir) == "dev"


def test_pin_nonexistent_raises(project_dir):
    with pytest.raises(FileNotFoundError):
        pin_profile(project_dir, "ghost")


def test_unpin_clears_pin(project_dir):
    _save(project_dir, "dev")
    pin_profile(project_dir, "dev")
    unpin_profile(project_dir)
    assert get_pinned(project_dir) is None


def test_unpin_when_nothing_pinned_is_noop(project_dir):
    unpin_profile(project_dir)  # should not raise
    assert get_pinned(project_dir) is None


def test_pin_overwrites_previous(project_dir):
    _save(project_dir, "dev")
    _save(project_dir, "prod")
    pin_profile(project_dir, "dev")
    pin_profile(project_dir, "prod")
    assert get_pinned(project_dir) == "prod"


def test_get_pinned_returns_none_when_no_file(project_dir):
    assert get_pinned(project_dir) is None
