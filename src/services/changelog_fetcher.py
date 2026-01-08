from __future__ import annotations
from typing import Optional
import httpx
import re


async def fetch_changelog_content(changelog_url: Optional[str], version: str) -> str:
    """
    Attempts to fetch changelog/release notes content from a given URL.
    Supports GitHub releases and tries to extract relevant release notes.
    Always returns a meaningful string for LLM consumption.
    """
    if not changelog_url:
        return "Changelog could not be fetched automatically. No official changelog source was found."
    
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            # GitHub releases page - try API first
            if "github.com" in changelog_url and "/releases" in changelog_url:
                # Extract owner/repo from URL
                match = re.search(r"github\.com/([^/]+)/([^/]+)", changelog_url)
                if match:
                    owner, repo = match.groups()
                    repo = repo.replace("/releases", "")
                    
                    # Try GitHub API to get latest release
                    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
                    try:
                        response = await client.get(api_url, headers={"Accept": "application/vnd.github+json"})
                        if response.status_code == 200:
                            releases = response.json()
                            # Find release matching the version
                            for release in releases[:10]:  # Check last 10 releases
                                tag_name = release.get("tag_name", "")
                                release_name = release.get("name", "")
                                # Match version with or without 'v' prefix
                                if version in tag_name or version in release_name or tag_name.lstrip("v") == version:
                                    body = release.get("body", "")
                                    if body:
                                        # Truncate if too long
                                        max_length = 2000
                                        if len(body) > max_length:
                                            body = body[:max_length] + "\n\n... (truncated)"
                                        return f"Release {tag_name or release_name}:\n\n{body}"
                            
                            # If no exact match, return the latest release
                            if releases:
                                latest_release = releases[0]
                                body = latest_release.get("body", "")
                                if body:
                                    max_length = 2000
                                    if len(body) > max_length:
                                        body = body[:max_length] + "\n\n... (truncated)"
                                    tag_name = latest_release.get("tag_name", "")
                                    return f"Latest Release {tag_name} (Note: Exact match for version {version} not found, showing latest release instead):\n\n{body}"
                    except Exception:
                        pass  # Fall back to scraping HTML
            
            # Fallback: Try to fetch the HTML page (for non-GitHub or if API fails)
            # This is a basic fallback - won't parse complex pages well
            response = await client.get(changelog_url)
            if response.status_code == 200:
                # Indicate that changelog exists at URL but couldn't be parsed
                return f"Changelog available at: {changelog_url}\n\nThe release notes exist but could not be automatically extracted. Visit the URL above for full details."
            
    except Exception:
        # Return informative message with source link
        if changelog_url:
            return f"Changelog could not be fetched automatically. Release notes may be available at: {changelog_url}"
    
    # Final fallback if everything failed
    return f"Changelog could not be fetched automatically. Release notes may be available at: {changelog_url}" if changelog_url else "Changelog could not be fetched automatically. No official changelog source was found."

