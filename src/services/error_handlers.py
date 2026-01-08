import logging

import httpx

from schemas.output import DependencyResult

logger = logging.getLogger(__name__)


def handle_registry_error(name: str, current: str, error: Exception, registry_name: str = "registry") -> DependencyResult:
    """
    Handles exceptions that occur when querying package registries.
    
    Args:
        name: The package name
        current: The current version string
        error: The exception that occurred
        registry_name: Name of the registry (e.g., "npm" or "PyPI") for logging
        
    Returns:
        DependencyResult with status "unknown" and appropriate error note
    """
    if isinstance(error, httpx.HTTPStatusError):
        # HTTP errors: 404 (not found), 500 (server error), etc.
        note = f"HTTP {error.response.status_code}: package not found or unavailable"
        return DependencyResult(
            name=name,
            current=current,
            latest="unknown",
            status="unknown",
            changelog_content=f"Changelog could not be fetched. Package not found or unavailable in {registry_name} registry (HTTP {error.response.status_code}).",
            note=note,
        )
    elif isinstance(error, httpx.TimeoutException):
        # Request took longer than 10 seconds
        return DependencyResult(
            name=name,
            current=current,
            latest="unknown",
            status="unknown",
            changelog_content=f"Changelog could not be fetched. Request to {registry_name} registry timed out.",
            note="Request timed out after 10 seconds",
        )
    elif isinstance(error, httpx.RequestError):
        # Network/connection errors (DNS, connection refused, etc.)
        return DependencyResult(
            name=name,
            current=current,
            latest="unknown",
            status="unknown",
            changelog_content=f"Changelog could not be fetched. Network error connecting to {registry_name} registry.",
            note=f"Network error: {type(error).__name__}",
        )
    else:
        # Catch truly unexpected errors and log them for debugging
        logger.error(f"Unexpected error querying {registry_name} for {name}: {error}", exc_info=True)
        return DependencyResult(
            name=name,
            current=current,
            latest="unknown",
            status="unknown",
            changelog_content=f"Changelog could not be fetched. An unexpected error occurred while querying {registry_name} registry.",
            note=f"Unexpected error: {type(error).__name__}",
        )

