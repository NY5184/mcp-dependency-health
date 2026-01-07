from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import httpx
from packaging.version import Version, InvalidVersion


@dataclass(frozen=True)
class RegistryResult:
    latest: str
    note: Optional[str] = None
    release_date: Optional[str] = None
    repository_url: Optional[str] = None
    homepage_url: Optional[str] = None
    changelog_url: Optional[str] = None
    description: Optional[str] = None


async def fetch_npm_latest(package_name: str) -> RegistryResult:
    """
    npm registry packument: https://registry.npmjs.org/<name>
    We'll read dist-tags.latest and extract contextual information.
    """
    url = f"https://registry.npmjs.org/{package_name}"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()

    dist_tags = data.get("dist-tags") or {}
    latest = dist_tags.get("latest")
    note = None
    
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
        
        note = "missing dist-tags.latest; used fallback"
    
    # Extract contextual information
    description = data.get("description")
    homepage = data.get("homepage")
    
    # Get repository URL
    repository = data.get("repository")
    repository_url = None
    if repository:
        if isinstance(repository, dict):
            repository_url = repository.get("url", "").replace("git+", "").replace(".git", "")
        elif isinstance(repository, str):
            repository_url = repository.replace("git+", "").replace(".git", "")
    
    # Get release date for the latest version
    release_date = None
    if latest and latest != "unknown":
        versions = data.get("versions") or {}
        version_data = versions.get(latest) or {}
        time_data = data.get("time") or {}
        release_date = time_data.get(latest)
    
    # Construct changelog URL (common patterns for npm packages)
    changelog_url = None
    if repository_url:
        # Try to construct a GitHub releases URL if it's a GitHub repo
        if "github.com" in repository_url:
            base_url = repository_url.replace("git://", "https://").replace("git@github.com:", "https://github.com/")
            changelog_url = f"{base_url}/releases"

    return RegistryResult(
        latest=str(latest),
        note=note,
        release_date=release_date,
        repository_url=repository_url,
        homepage_url=homepage,
        changelog_url=changelog_url,
        description=description
    )


async def fetch_pypi_latest(package_name: str) -> RegistryResult:
    """
    PyPI JSON API: https://pypi.org/pypi/<project>/json
    We'll use info.version as the latest release string and extract contextual information.
    """
    url = f"https://pypi.org/pypi/{package_name}/json"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()

    info = data.get("info") or {}
    latest = info.get("version") or "unknown"
    
    # Extract contextual information
    description = info.get("summary")  # PyPI uses "summary" field
    homepage = info.get("home_page") or info.get("package_url")
    
    # Get URLs (PyPI provides structured URLs)
    project_urls = info.get("project_urls") or {}
    
    # Look for changelog in multiple common keys
    changelog_url = (
        project_urls.get("Changelog") or 
        project_urls.get("Change Log") or
        project_urls.get("Release Notes") or
        project_urls.get("Releases") or
        project_urls.get("Changes")
    )
    
    # Look for repository URL
    repository_url = (
        project_urls.get("Source") or
        project_urls.get("Repository") or
        project_urls.get("Source Code") or
        project_urls.get("Code") or
        info.get("project_url")
    )
    
    # If no explicit changelog, try to construct one from repository
    if not changelog_url and repository_url:
        if "github.com" in repository_url:
            changelog_url = f"{repository_url.rstrip('/')}/releases"
        elif "gitlab.com" in repository_url:
            changelog_url = f"{repository_url.rstrip('/')}/releases"
    
    # Get release date from releases data
    release_date = None
    releases = data.get("releases") or {}
    if latest and latest != "unknown" and latest in releases:
        release_info = releases[latest]
        if release_info and len(release_info) > 0:
            # Get upload_time from the first file in the release
            release_date = release_info[0].get("upload_time")
    
    return RegistryResult(
        latest=str(latest),
        release_date=release_date,
        repository_url=repository_url,
        homepage_url=homepage,
        changelog_url=changelog_url,
        description=description
    )
