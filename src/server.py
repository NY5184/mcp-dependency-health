from __future__ import annotations

import logging
from typing import List

import httpx
from mcp.server.fastmcp import FastMCP

from schemas.input import DependencyHealthInput, Ecosystem
from schemas.output import DependencyHealthOutput, DependencyResult

from utils.file_finder import find_dependency_files
from utils.parsers import parse_package_json, parse_requirements_txt
from utils.versions import is_prerelease, is_up_to_date

from src.services.registry_clients import fetch_npm_latest, fetch_pypi_latest

# Configure logging for unexpected errors
logger = logging.getLogger(__name__)

mcp = FastMCP("Dependency Health Checker MCP")


@mcp.tool()
async def dependency_health_check(payload: dict) -> dict:
    """
    Performs a comprehensive health check on project dependencies.
    
    Detects the ecosystem (JavaScript/Python), parses dependency files (package.json
    or requirements.txt), queries package registries for latest versions, and compares
    them against current versions to determine if dependencies are up-to-date or outdated.
    
    Input: DependencyHealthInput as dict (project_path, ecosystem)
    Output: DependencyHealthOutput as dict (list of dependency results with status)
    """
    inp = DependencyHealthInput(**payload)
    files = find_dependency_files(inp.project_path)

    # Decide ecosystem
    eco = inp.ecosystem
    if eco == Ecosystem.auto:
        if files["package_json"]:
            eco = Ecosystem.javascript
        elif files["requirements_txt"]:
            eco = Ecosystem.python

    results: List[DependencyResult] = []

    if eco == Ecosystem.javascript and files["package_json"]:
        deps = parse_package_json(files["package_json"])
        for name, current in deps.items():
            try:
                reg = await fetch_npm_latest(name)
                latest = reg.latest

                note_parts = []
                if reg.note:
                    note_parts.append(reg.note)
                if is_prerelease(latest):
                    note_parts.append(f"{latest} is pre-release (from registry)")

                ok, cmp_note = is_up_to_date(current, latest)
                if cmp_note:
                    note_parts.append(cmp_note)

                status = "up-to-date" if ok else "outdated"
                results.append(
                    DependencyResult(
                        name=name,
                        current=current,
                        latest=latest,
                        status=status,
                        note="; ".join(note_parts) or None,
                    )
                )
            except httpx.HTTPStatusError as e:
                # HTTP errors: 404 (not found), 500 (server error), etc.
                note = f"HTTP {e.response.status_code}: package not found or unavailable"
                results.append(
                    DependencyResult(
                        name=name,
                        current=current,
                        latest="unknown",
                        status="unknown",
                        note=note,
                    )
                )
            except httpx.TimeoutException:
                # Request took longer than 10 seconds
                results.append(
                    DependencyResult(
                        name=name,
                        current=current,
                        latest="unknown",
                        status="unknown",
                        note="Request timed out after 10 seconds",
                    )
                )
            except httpx.RequestError as e:
                # Network/connection errors (DNS, connection refused, etc.)
                results.append(
                    DependencyResult(
                        name=name,
                        current=current,
                        latest="unknown",
                        status="unknown",
                        note=f"Network error: {type(e).__name__}",
                    )
                )
            except Exception as e:
                # Catch truly unexpected errors and log them for debugging
                logger.error(f"Unexpected error querying npm for {name}: {e}", exc_info=True)
                results.append(
                    DependencyResult(
                        name=name,
                        current=current,
                        latest="unknown",
                        status="unknown",
                        note=f"Unexpected error: {type(e).__name__}",
                    )
                )

    elif eco == Ecosystem.python and files["requirements_txt"]:
        deps = parse_requirements_txt(files["requirements_txt"])
        for name, spec in deps:
            current = f"{name}{spec}" if spec else name
            try:
                reg = await fetch_pypi_latest(name)
                latest = reg.latest

                note_parts = []
                if reg.note:
                    note_parts.append(reg.note)
                if is_prerelease(latest):
                    note_parts.append(f"{latest} is pre-release (from registry)")

                ok, cmp_note = is_up_to_date(spec or "", latest) if spec else (False, "no pinned version")
                if cmp_note:
                    note_parts.append(cmp_note)

                status = "up-to-date" if ok else "outdated"
                results.append(
                    DependencyResult(
                        name=name,
                        current=current,
                        latest=latest,
                        status=status,
                        note="; ".join(note_parts) or None,
                    )
                )
            except httpx.HTTPStatusError as e:
                # HTTP errors: 404 (not found), 500 (server error), etc.
                note = f"HTTP {e.response.status_code}: package not found or unavailable"
                results.append(
                    DependencyResult(
                        name=name,
                        current=current,
                        latest="unknown",
                        status="unknown",
                        note=note,
                    )
                )
            except httpx.TimeoutException:
                # Request took longer than 10 seconds
                results.append(
                    DependencyResult(
                        name=name,
                        current=current,
                        latest="unknown",
                        status="unknown",
                        note="Request timed out after 10 seconds",
                    )
                )
            except httpx.RequestError as e:
                # Network/connection errors (DNS, connection refused, etc.)
                results.append(
                    DependencyResult(
                        name=name,
                        current=current,
                        latest="unknown",
                        status="unknown",
                        note=f"Network error: {type(e).__name__}",
                    )
                )
            except Exception as e:
                # Catch truly unexpected errors and log them for debugging
                logger.error(f"Unexpected error querying PyPI for {name}: {e}", exc_info=True)
                results.append(
                    DependencyResult(
                        name=name,
                        current=current,
                        latest="unknown",
                        status="unknown",
                        note=f"Unexpected error: {type(e).__name__}",
                    )
                )
    else:
        # nothing found
        results.append(
            DependencyResult(
                name="(no dependency file found)",
                current="",
                latest="",
                status="unknown",
                note="expected package.json or requirements.txt in project_path",
            )
        )

    out = DependencyHealthOutput(dependencies=results)
    return out.model_dump()


def main() -> None:
    """
    Entry point for the MCP server. Starts the FastMCP server in stdio mode.
    """
    # stdio server
    mcp.run()


if __name__ == "__main__":
    main()
