from __future__ import annotations

import asyncio
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


async def check_javascript_dependencies(package_json_path) -> List[DependencyResult]:
    """
    Checks JavaScript dependencies defined in package.json.
    """
    deps = parse_package_json(package_json_path)
    
    async def check_single_dependency(name: str, current: str) -> DependencyResult:
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

            return DependencyResult(
                name=name,
                current=current,
                latest=latest,
                status="up-to-date" if ok else "outdated",
                note="; ".join(note_parts) or None,
                release_date=reg.release_date,
                changelog_content=reg.changelog_content,
                description=reg.description,
            )
        except Exception as e:
            return handle_registry_error(name, current, e, "npm")
    
    # Run all dependency checks in parallel
    tasks = [check_single_dependency(name, current) for name, current in deps.items()]
    results = await asyncio.gather(*tasks)
    
    return list(results)


async def check_python_dependencies(requirements_path) -> List[DependencyResult]:
    """
    Checks Python dependencies defined in requirements.txt.
    """
    deps = parse_requirements_txt(requirements_path)
    
    async def check_single_dependency(name: str, spec: str) -> DependencyResult:
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

            return DependencyResult(
                name=name,
                current=current,
                latest=latest,
                status="up-to-date" if ok else "outdated",
                note="; ".join(note_parts) or None,
                release_date=reg.release_date,
                changelog_content=reg.changelog_content,
                description=reg.description,
            )
        except Exception as e:
            return handle_registry_error(name, current, e, "PyPI")
    
    # Run all dependency checks in parallel
    tasks = [check_single_dependency(name, spec) for name, spec in deps]
    results = await asyncio.gather(*tasks)
    
    return list(results)


@mcp.tool()
async def dependency_health_check(payload: dict) -> dict:
    """
Analyzes project dependencies and provides contextual data to assess upgrade impact.

Supports: npm (package.json) and pip (requirements.txt) only.
Other package managers (Poetry, Pipenv, Cargo, Go modules, Maven, Gradle, Composer, NuGet, etc.) are not supported.

Returns for each dependency: name, current version, latest version, status, changelog_content
(actual release notes or explanatory message), description, and release_date.

**When to use this tool:**
- User asks about dependency versions/updates in a specific project
- User requests dependency health check or audit
- Before suggesting upgrades that require inspecting actual project dependencies

**How to analyze results:**
1. Use `changelog_content` to identify specific changes, bug fixes, breaking changes
2. State that assessment is limited if changelog could not be fetched
3. Direct user to source URL if mentioned in `changelog_content`
4. Do not infer changes not explicitly stated in `changelog_content`
5. Use description and release_date to assess maturity/stability
6. Consider major version gaps as potential breaking change indicators

Provide recommendations (low/medium/high impact) based on risk, scope, and maintenance
implications—not just version differences.

    """
    # Validate and normalize input
    inp = DependencyHealthInput(**payload)

    # Locate dependency files
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
        results = await check_javascript_dependencies(files["package_json"])

    elif eco == Ecosystem.python and files["requirements_txt"]:
        results = await check_python_dependencies(files["requirements_txt"])

    else:
        # No supported dependency file found
        supported_managers = "npm (package.json) and pip (requirements.txt)"
        unsupported_examples = "Poetry, Pipenv, Cargo, Go modules, Maven/Gradle, Composer, NuGet, etc."
        results.append(
            DependencyResult(
                name="(no supported dependency file found)",
                current="",
                latest="",
                status="unknown",
                changelog_content="No dependency analysis performed. This project uses an unsupported or missing dependency manager.",
                note=f"This project uses an unsupported or missing dependency manager. Currently supported: {supported_managers}. Unsupported package managers include: {unsupported_examples}",
            )
        )

    out = DependencyHealthOutput(dependencies=results)
    return out.model_dump()


def main() -> None:
    """
    Entry point for the MCP server. Starts the FastMCP server in stdio mode.
    """
    mcp.run()


if __name__ == "__main__":
    main()
