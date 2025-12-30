from utils.versions import is_up_to_date, is_prerelease

def test_outdated():
    ok, _ = is_up_to_date("17.0.2", "18.2.0")
    assert ok is False

def test_up_to_date():
    ok, _ = is_up_to_date("4.17.21", "4.17.21")
    assert ok is True

def test_npm_range():
    ok, _ = is_up_to_date("^17.0.2", "17.0.2")
    assert ok is True

def test_python_range():
    ok, _ = is_up_to_date(">=1.0", "0.9")
    assert ok is False

def test_prerelease_detected():
    assert is_prerelease("1.3.0-beta.1") is True
