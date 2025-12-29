from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
import httpx


@dataclass(frozen=True)
class RegistryResult:
    latest: str
    note: Optional[str] = None


async def fetch_npm_latest(package_name: str) -> RegistryResult:
    """
    npm registry packument: https://registry.npmjs.org/<name>
    We'll read dist-tags.latest.
    """
    url = f"https://registry.npmjs.org/{package_name}"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()

    dist_tags = data.get("dist-tags") or {}
    latest = dist_tags.get("latest")
    if not latest:
        # fallback: no dist-tag
        versions = list((data.get("versions") or {}).keys())
        latest = sorted(versions)[-1] if versions else "unknown"
        return RegistryResult(latest=latest, note="missing dist-tags.latest; used fallback")

    return RegistryResult(latest=str(latest))


async def fetch_pypi_latest(package_name: str) -> RegistryResult:
    """
    PyPI JSON API: https://pypi.org/pypi/<project>/json
    We'll use info.version as the latest release string.
    """
    url = f"https://pypi.org/pypi/{package_name}/json"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()

    info = data.get("info") or {}
    latest = info.get("version") or "unknown"
    return RegistryResult(latest=str(latest))
