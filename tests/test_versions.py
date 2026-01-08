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

def test_npm_caret_range_with_newer_patch():
    """Test that ^18.0.0 is up-to-date when latest is 18.2.0 (satisfies range)"""
    ok, _ = is_up_to_date("^18.0.0", "18.2.0")
    assert ok is True, "18.2.0 should satisfy ^18.0.0 range (>=18.0.0,<19.0.0)"

def test_npm_caret_range_with_newer_major():
    """Test that ^18.0.0 is outdated when latest is 19.0.0 (doesn't satisfy range)"""
    ok, _ = is_up_to_date("^18.0.0", "19.0.0")
    assert ok is False, "19.0.0 should NOT satisfy ^18.0.0 range (>=18.0.0,<19.0.0)"

def test_npm_tilde_range():
    """Test that ~18.0.0 allows patch updates but not minor updates"""
    ok1, _ = is_up_to_date("~18.0.0", "18.0.5")
    assert ok1 is True, "18.0.5 should satisfy ~18.0.0 range (>=18.0.0,<18.1.0)"
    
    ok2, _ = is_up_to_date("~18.0.0", "18.1.0")
    assert ok2 is False, "18.1.0 should NOT satisfy ~18.0.0 range (>=18.0.0,<18.1.0)"

def test_python_range():
    ok, _ = is_up_to_date(">=1.0", "0.9")
    assert ok is False

def test_prerelease_detected():
    assert is_prerelease("1.3.0-beta.1") is True
