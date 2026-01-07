import pytest
from src.services import registry_clients

@pytest.mark.asyncio
async def test_fetch_npm_latest(monkeypatch):
    async def fake_get(*args, **kwargs):
        class R:
            def raise_for_status(self): pass
            def json(self):
                return {
                    "dist-tags": {"latest": "18.2.0"},
                    "description": "React is a JavaScript library for building user interfaces.",
                    "homepage": "https://react.dev/",
                    "repository": {
                        "type": "git",
                        "url": "git+https://github.com/facebook/react.git"
                    },
                    "time": {
                        "18.2.0": "2022-06-14T16:55:41.036Z"
                    },
                    "versions": {
                        "18.2.0": {}
                    }
                }
        return R()

    monkeypatch.setattr(registry_clients.httpx.AsyncClient, "get", fake_get)
    res = await registry_clients.fetch_npm_latest("react")
    assert res.latest == "18.2.0"
    assert res.description == "React is a JavaScript library for building user interfaces."
    assert res.homepage_url == "https://react.dev/"
    assert res.repository_url == "https://github.com/facebook/react"
    assert res.release_date == "2022-06-14T16:55:41.036Z"
    assert res.changelog_url == "https://github.com/facebook/react/releases"

@pytest.mark.asyncio
async def test_fetch_pypi_latest(monkeypatch):
    async def fake_get(*args, **kwargs):
        class R:
            def raise_for_status(self): pass
            def json(self):
                return {
                    "info": {
                        "version": "2.31.0",
                        "summary": "Python HTTP for Humans.",
                        "home_page": "https://requests.readthedocs.io",
                        "project_urls": {
                            "Source": "https://github.com/psf/requests",
                            "Changelog": "https://github.com/psf/requests/blob/main/HISTORY.md"
                        }
                    },
                    "releases": {
                        "2.31.0": [
                            {"upload_time": "2023-05-22T14:52:48"}
                        ]
                    }
                }
        return R()

    monkeypatch.setattr(registry_clients.httpx.AsyncClient, "get", fake_get)
    res = await registry_clients.fetch_pypi_latest("requests")
    assert res.latest == "2.31.0"
    assert res.description == "Python HTTP for Humans."
    assert res.homepage_url == "https://requests.readthedocs.io"
    assert res.repository_url == "https://github.com/psf/requests"
    assert res.changelog_url == "https://github.com/psf/requests/blob/main/HISTORY.md"
    assert res.release_date == "2023-05-22T14:52:48"
