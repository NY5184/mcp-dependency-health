from utils.parsers import parse_requirements_txt

def test_exact_version(tmp_path):
    p = tmp_path / "requirements.txt"
    p.write_text("requests==2.31.0")
    deps = parse_requirements_txt(p)
    assert deps == [("requests", "==2.31.0")]

def test_range_version(tmp_path):
    p = tmp_path / "requirements.txt"
    p.write_text("numpy>=1.24")
    deps = parse_requirements_txt(p)
    assert deps == [("numpy", ">=1.24")]

def test_no_version(tmp_path):
    p = tmp_path / "requirements.txt"
    p.write_text("flask")
    deps = parse_requirements_txt(p)
    assert deps == [("flask", "")]

def test_ignore_comments(tmp_path):
    p = tmp_path / "requirements.txt"
    p.write_text("# comment\n\nflask")
    deps = parse_requirements_txt(p)
    assert deps == [("flask", "")]
