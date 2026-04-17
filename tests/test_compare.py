import pytest
from pathlib import Path
from stashenv.store import save_profile
from stashenv.compare import compare_profiles, format_compare


@pytest.fixture
def project_dir(tmp_path):
    return str(tmp_path)


def _save(project_dir, name, content, password="pass"):
    save_profile(project_dir, name, content, password)


def test_compare_equal_profiles(project_dir):
    _save(project_dir, "a", "KEY=value\nFOO=bar\n")
    _save(project_dir, "b", "KEY=value\nFOO=bar\n")
    report = compare_profiles(project_dir, "a", "pass", project_dir, "b", "pass")
    assert all(info["status"] == "equal" for info in report.values())


def test_compare_differs(project_dir):
    _save(project_dir, "a", "KEY=one\n")
    _save(project_dir, "b", "KEY=two\n")
    report = compare_profiles(project_dir, "a", "pass", project_dir, "b", "pass")
    assert report["KEY"]["status"] == "differs"
    assert report["KEY"]["a"] == "one"
    assert report["KEY"]["b"] == "two"


def test_compare_only_in_a(project_dir):
    _save(project_dir, "a", "KEY=val\nEXTRA=x\n")
    _save(project_dir, "b", "KEY=val\n")
    report = compare_profiles(project_dir, "a", "pass", project_dir, "b", "pass")
    assert report["EXTRA"]["status"] == "only_in_a"


def test_compare_only_in_b(project_dir):
    _save(project_dir, "a", "KEY=val\n")
    _save(project_dir, "b", "KEY=val\nNEW=y\n")
    report = compare_profiles(project_dir, "a", "pass", project_dir, "b", "pass")
    assert report["NEW"]["status"] == "only_in_b"


def test_compare_across_projects(tmp_path):
    dir_a = str(tmp_path / "proj_a")
    dir_b = str(tmp_path / "proj_b")
    Path(dir_a).mkdir()
    Path(dir_b).mkdir()
    save_profile(dir_a, "env", "X=1\n", "pa")
    save_profile(dir_b, "env", "X=2\n", "pb")
    report = compare_profiles(dir_a, "env", "pa", dir_b, "env", "pb")
    assert report["X"]["status"] == "differs"


def test_format_compare_hides_values(project_dir):
    _save(project_dir, "a", "KEY=secret\n")
    _save(project_dir, "b", "KEY=other\n")
    report = compare_profiles(project_dir, "a", "pass", project_dir, "b", "pass")
    output = format_compare(report, reveal=False)
    assert "secret" not in output
    assert "other" not in output
    assert "differs" in output or "~" in output


def test_format_compare_reveals_values(project_dir):
    _save(project_dir, "a", "KEY=secret\n")
    _save(project_dir, "b", "KEY=secret\n")
    report = compare_profiles(project_dir, "a", "pass", project_dir, "b", "pass")
    output = format_compare(report, reveal=True)
    assert "secret" in output
