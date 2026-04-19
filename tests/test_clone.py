import pytest
from pathlib import Path
from stashenv.clone import clone_profile, clone_all_profiles
from stashenv.store import save_profile, load_profile, list_profiles


@pytest.fixture
def project_dir(tmp_path):
    return tmp_path


def _save(project: Path, name: str, content: str, password: str = "pass"):
    save_profile(project, name, content, password)


def test_clone_within_same_project(project_dir):
    src = project_dir / "src"
    dst = project_dir / "dst"
    _save(src, "dev", "KEY=value\n")
    clone_profile(src, "dev", dst, "dev-copy", "pass")
    result = load_profile(dst, "dev-copy", "pass")
    assert result == "KEY=value\n"


def test_clone_across_projects(project_dir):
    src = project_dir / "proj_a"
    dst = project_dir / "proj_b"
    _save(src, "prod", "DB=postgres\n")
    clone_profile(src, "prod", dst, "prod", "pass")
    assert "prod" in list_profiles(dst)


def test_clone_with_new_password(project_dir):
    src = project_dir / "src"
    dst = project_dir / "dst"
    _save(src, "staging", "HOST=localhost\n")
    clone_profile(src, "staging", dst, "staging", "pass", dst_password="newpass")
    result = load_profile(dst, "staging", "newpass")
    assert "HOST=localhost" in result


def test_clone_with_new_password_old_password_fails(project_dir):
    """Ensure the old password cannot decrypt a profile cloned with a new password."""
    src = project_dir / "src"
    dst = project_dir / "dst"
    _save(src, "staging", "HOST=localhost\n")
    clone_profile(src, "staging", dst, "staging", "pass", dst_password="newpass")
    with pytest.raises(Exception):
        load_profile(dst, "staging", "pass")


def test_clone_nonexistent_raises(project_dir):
    src = project_dir / "src"
    dst = project_dir / "dst"
    with pytest.raises(FileNotFoundError):
        clone_profile(src, "missing", dst, "missing", "pass")


def test_clone_conflict_raises(project_dir):
    src = project_dir / "src"
    dst = project_dir / "dst"
    _save(src, "dev", "A=1\n")
    _save(dst, "dev", "B=2\n")
    with pytest.raises(FileExistsError):
        clone_profile(src, "dev", dst, "dev", "pass")


def test_clone_all_profiles(project_dir):
    src = project_dir / "src"
    dst = project_dir / "dst"
    for name in ["dev", "staging", "prod"]:
        _save(src, name, f"ENV={name}\n")
    cloned = clone_all_profiles(src, dst, "pass")
    assert set(cloned) == {"dev", "staging", "prod"}
    assert set(list_profiles(dst)) == {"dev", "staging", "prod"}


def test_clone_all_skip_existing(project_dir):
    src = project_dir / "src"
    dst = project_dir / "dst"
    _save(src, "dev", "KEY=1\n")
    _save(src, "prod", "KEY=2\n")
    _save(dst, "dev", "KEY=existing\n")
    cloned = clone_all_profiles(src, dst, "pass", skip_existing=True)
    assert cloned == ["prod"]
