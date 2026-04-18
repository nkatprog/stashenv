import pytest
from pathlib import Path
from stashenv.backup import create_backup, restore_backup, list_backup_profiles
from stashenv.store import save_profile, load_profile, list_profiles


@pytest.fixture
def project_dir(tmp_path):
    return str(tmp_path / "myproject")


def _save(project_dir, name, content, password="secret"):
    save_profile(project_dir, name, content, password)


def test_create_backup_and_list(project_dir, tmp_path):
    _save(project_dir, "dev", "DB=dev\nDEBUG=true")
    _save(project_dir, "prod", "DB=prod\nDEBUG=false")
    backup_file = str(tmp_path / "backup.enc")
    count = create_backup(project_dir, "secret", backup_file)
    assert count == 2
    assert Path(backup_file).exists()


def test_list_backup_profiles(project_dir, tmp_path):
    _save(project_dir, "dev", "A=1")
    _save(project_dir, "staging", "A=2")
    backup_file = str(tmp_path / "backup.enc")
    create_backup(project_dir, "secret", backup_file)
    names = list_backup_profiles(backup_file, "secret")
    assert sorted(names) == ["dev", "staging"]


def test_restore_backup(project_dir, tmp_path):
    _save(project_dir, "dev", "KEY=value")
    backup_file = str(tmp_path / "backup.enc")
    create_backup(project_dir, "secret", backup_file)

    new_project = str(tmp_path / "newproject")
    restored = restore_backup(new_project, "secret", backup_file)
    assert "dev" in restored
    content = load_profile(new_project, "dev", "secret")
    assert "KEY=value" in content


def test_restore_conflict_raises(project_dir, tmp_path):
    _save(project_dir, "dev", "KEY=1")
    backup_file = str(tmp_path / "backup.enc")
    create_backup(project_dir, "secret", backup_file)
    with pytest.raises(FileExistsError):
        restore_backup(project_dir, "secret", backup_file, overwrite=False)


def test_restore_overwrite(project_dir, tmp_path):
    _save(project_dir, "dev", "KEY=old")
    backup_file = str(tmp_path / "backup.enc")
    create_backup(project_dir, "secret", backup_file)
    _save(project_dir, "dev", "KEY=changed")
    restore_backup(project_dir, "secret", backup_file, overwrite=True)
    content = load_profile(project_dir, "dev", "secret")
    assert "KEY=old" in content


def test_create_backup_no_profiles_raises(project_dir, tmp_path):
    backup_file = str(tmp_path / "backup.enc")
    with pytest.raises(ValueError, match="No profiles"):
        create_backup(project_dir, "secret", backup_file)


def test_wrong_password_on_restore(project_dir, tmp_path):
    _save(project_dir, "dev", "A=1")
    backup_file = str(tmp_path / "backup.enc")
    create_backup(project_dir, "secret", backup_file)
    with pytest.raises(Exception):
        list_backup_profiles(backup_file, "wrongpass")
