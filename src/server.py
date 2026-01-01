from __future__ import annotations

from typing import List

from mcp.server.fastmcp import FastMCP

from schemas.input import DependencyHealthInput, Ecosystem
from schemas.output import DependencyHealthOutput, DependencyResult

from utils.file_finder import find_dependency_files
from utils.parsers import parse_package_json, parse_requirements_txt
from utils.versions import is_prerelease, is_up_to_date

from src.services.registry_clients import fetch_npm_latest, fetch_pypi_latest
from src.services.error_handlers import handle_registry_error

mcp = FastMCP("Dependency Health Checker MCP")


@mcp.tool()
async def dependency_health_check(payload: dict) -> dict:
    """
    Performs a comprehensive health check on project dependencies.
    
    Detects the ecosystem (JavaScript/Python), parses dependency files (package.json
    or requirements.txt), queries package registries for latest versions, and compares
    them against current versions to determine if dependencies are up-to-date or outdated.
    
    Input: DependencyHealthInput as dict (project_path, ecosystem  optional)
    Output: DependencyHealthOutput as dict (list of dependency results with status)
    """
    # Validate and normalize input: ensures project_path exists, is a directory, and resolves to absolute path
    inp = DependencyHealthInput(**payload)
    # Locate dependency manifest files (package.json and requirements.txt) in the project directory
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
        # Extract all dependencies from package.json (includes dependencies, devDependencies, peerDependencies, optionalDependencies)
        deps = parse_package_json(files["package_json"])
        for name, current in deps.items():
            try:
                # Query npm registry to get the latest version of this package
                reg = await fetch_npm_latest(name)
                latest = reg.latest

                note_parts = []
                if reg.note:
                    note_parts.append(reg.note)
                # Check if latest version is a prerelease (e.g., "1.2.3-beta.1")
                if is_prerelease(latest):
                    note_parts.append(f"{latest} is pre-release (from registry)")

                # Compare current version spec (e.g., "^17.0.2") against latest version to check if up-to-date
                ok, cmp_note = is_up_to_date(current, latest)
                if cmp_note:
                    note_parts.append(cmp_note)

                status = "up-to-date" if ok else "outdated"
                # Create result object with package info and comparison status
                results.append(
                    DependencyResult(
                        name=name,
                        current=current,
                        latest=latest,
                        status=status,
                        note="; ".join(note_parts) or None,
                    )
                )
            except Exception as e:
                # Handle registry errors (HTTP errors, timeouts, network issues)
                results.append(handle_registry_error(name, current, e, "npm"))

    elif eco == Ecosystem.python and files["requirements_txt"]:
        # Parse requirements.txt to extract package names and version specifiers
        deps = parse_requirements_txt(files["requirements_txt"])
        for name, spec in deps:
            current = f"{name}{spec}" if spec else name
            try:
                # Query PyPI registry to get the latest version of this package
                reg = await fetch_pypi_latest(name)
                latest = reg.latest

                note_parts = []
                if reg.note:
                    note_parts.append(reg.note)
                # Check if latest version is a prerelease (e.g., "1.2.3-beta.1")
                if is_prerelease(latest):
                    note_parts.append(f"{latest} is pre-release (from registry)")

                # Compare version spec against latest; handle packages without pinned versions
                ok, cmp_note = is_up_to_date(spec or "", latest) if spec else (False, "no pinned version")
                if cmp_note:
                    note_parts.append(cmp_note)

                status = "up-to-date" if ok else "outdated"
                # Create result object with package info and comparison status
                results.append(
                    DependencyResult(
                        name=name,
                        current=current,
                        latest=latest,
                        status=status,
                        note="; ".join(note_parts) or None,
                    )
                )
            except Exception as e:
                # Handle registry errors (HTTP errors, timeouts, network issues)
                results.append(handle_registry_error(name, current, e, "PyPI"))
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

    # Convert output model to dictionary for MCP response
    out = DependencyHealthOutput(dependencies=results)
    return out.model_dump()


def main() -> None:
    """
    Entry point for the MCP server. Starts the FastMCP server in stdio mode.
    """
    # Start the MCP server in stdio mode for communication with MCP clients
    mcp.run()


if __name__ == "__main__":
    main()
