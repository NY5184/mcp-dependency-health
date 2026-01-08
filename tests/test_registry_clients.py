import pytest
from src.services import registry_clients

@pytest.mark.asyncio
async def test_fetch_npm_latest(monkeypatch):
    async def fake_get(self, url, **kwargs):
        class R:
            def __init__(self, url):
                self.url = url
                self.status_code = 200
            def raise_for_status(self): pass
            def json(self):
                # Registry API response
                if "registry.npmjs.org" in self.url:
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
                # GitHub API response
                elif "api.github.com" in self.url:
                    return [
                        {
                            "tag_name": "v18.2.0",
                            "name": "v18.2.0",
                            "body": "## Fixes\n- Fix memory leak in development mode\n- Fix Suspense bug"
                        }
                    ]
                return {}
        return R(url)

    monkeypatch.setattr(registry_clients.httpx.AsyncClient, "get", fake_get)
    res = await registry_clients.fetch_npm_latest("react")
    assert res.latest == "18.2.0"
    assert res.description == "React is a JavaScript library for building user interfaces."
    assert res.release_date == "2022-06-14T16:55:41.036Z"
    # changelog_content is always a string (never None)
    assert isinstance(res.changelog_content, str)
    assert len(res.changelog_content) > 0
    assert "Fixes" in res.changelog_content

@pytest.mark.asyncio
async def test_fetch_pypi_latest(monkeypatch):
    async def fake_get(self, url, **kwargs):
        class R:
            def __init__(self, url):
                self.url = url
                self.status_code = 200
            def raise_for_status(self): pass
            def json(self):
                # PyPI API response
                if "pypi.org" in self.url:
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
                # GitHub/GitLab changelog - return fallback message
                return {}
        return R(url)

    monkeypatch.setattr(registry_clients.httpx.AsyncClient, "get", fake_get)
    res = await registry_clients.fetch_pypi_latest("requests")
    assert res.latest == "2.31.0"
    assert res.description == "Python HTTP for Humans."
    assert res.release_date == "2023-05-22T14:52:48"
    # changelog_content is always a string (never None)
    assert isinstance(res.changelog_content, str)
    assert len(res.changelog_content) > 0
    # For this test, since it's a non-GitHub releases URL, it should have a fallback message
    assert "Changelog" in res.changelog_content
