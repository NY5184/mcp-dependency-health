import json
from utils.parsers import parse_package_json

def test_parse_dependencies(tmp_path):
    data = {"dependencies": {"react": "17.0.2"}}
    path = tmp_path / "package.json"
    path.write_text(json.dumps(data))
    deps = parse_package_json(path)
    assert deps == {"react": "17.0.2"}

def test_parse_dev_dependencies(tmp_path):
    data = {"devDependencies": {"eslint": "^8.0.0"}}
    path = tmp_path / "package.json"
    path.write_text(json.dumps(data))
    deps = parse_package_json(path)
    assert deps == {"eslint": "^8.0.0"}
