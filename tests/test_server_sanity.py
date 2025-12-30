import json
import pytest
from src.server import dependency_health_check

@pytest.mark.asyncio
async def test_server_sanity_js(tmp_path, monkeypatch):
    (tmp_path / "package.json").write_text(
        json.dumps({"dependencies": {"react": "17.0.2"}})
    )

    async def fake_fetch(name):
        class R:
            latest = "18.2.0"
            note = None
        return R()

    monkeypatch.setattr(
        "src.server.fetch_npm_latest", fake_fetch
    )

    result = await dependency_health_check({
        "project_path": str(tmp_path),
        "ecosystem": "javascript"
    })

    deps = result["dependencies"]
    assert len(deps) == 1
    assert deps[0]["name"] == "react"
    assert "status" in deps[0]
