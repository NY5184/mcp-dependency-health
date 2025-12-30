from utils.file_finder import find_dependency_files

def test_find_package_json(tmp_path):
    (tmp_path / "package.json").write_text("{}")
    files = find_dependency_files(str(tmp_path))
    assert files["package_json"] is not None
    assert files["requirements_txt"] is None

def test_find_requirements_txt(tmp_path):
    (tmp_path / "requirements.txt").write_text("")
    files = find_dependency_files(str(tmp_path))
    assert files["requirements_txt"] is not None
    assert files["package_json"] is None

def test_find_nothing(tmp_path):
    files = find_dependency_files(str(tmp_path))
    assert files["package_json"] is None
    assert files["requirements_txt"] is None
