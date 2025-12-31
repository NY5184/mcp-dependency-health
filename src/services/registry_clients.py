from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import httpx
from packaging.version import Version, InvalidVersion


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
        # fallback: no dist-tag - use semantic version sorting
        version_strings = list((data.get("versions") or {}).keys())
        if version_strings:
            # Parse versions and filter out invalid ones
            valid_versions = []
            for v in version_strings:
                try:
                    valid_versions.append(Version(v))
                except InvalidVersion:
                    # Skip invalid version strings
                    continue
            
            if valid_versions:
                # Get the highest semantic version
                latest = str(max(valid_versions))
            else:
                # All versions were invalid, fall back to string sort
                latest = sorted(version_strings)[-1]
        else:
            latest = "unknown"
        
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
