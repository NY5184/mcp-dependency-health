import pytest
from src.services import registry_clients

@pytest.mark.asyncio
async def test_fetch_npm_latest(monkeypatch):
    async def fake_get(*args, **kwargs):
        class R:
            def raise_for_status(self): pass
            def json(self):
                return {"dist-tags": {"latest": "18.2.0"}}
        return R()

    monkeypatch.setattr(registry_clients.httpx.AsyncClient, "get", fake_get)
    res = await registry_clients.fetch_npm_latest("react")
    assert res.latest == "18.2.0"

@pytest.mark.asyncio
async def test_fetch_pypi_latest(monkeypatch):
    async def fake_get(*args, **kwargs):
        class R:
            def raise_for_status(self): pass
            def json(self):
                return {"info": {"version": "2.31.0"}}
        return R()

    monkeypatch.setattr(registry_clients.httpx.AsyncClient, "get", fake_get)
    res = await registry_clients.fetch_pypi_latest("requests")
    assert res.latest == "2.31.0"
