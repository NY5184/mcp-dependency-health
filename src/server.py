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
                repository_url=reg.repository_url,
                homepage_url=reg.homepage_url,
                changelog_url=reg.changelog_url,
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
                repository_url=reg.repository_url,
                homepage_url=reg.homepage_url,
                changelog_url=reg.changelog_url,
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

The tool detects JavaScript (package.json) or Python (requirements.txt) projects,
queries npm/PyPI registries, and returns dependency health signals including version
gaps, release dates, descriptions, and relevant URLs.

Before calling this tool, ensure the input payload matches the expected input
schema

After calling this tool, the LLM may use the data to reason about whether and how
to upgrade dependencies. Consider the package description to understand its role,
release dates to assess stability, and major version gaps as potential indicators
of breaking changes. Changelog and repository URLs are provided for optional
deeper investigation.

The tool does not make upgrade decisions. The LLM is expected to provide a
high-level, reasoned recommendation (low / medium / high impact), beyond simple
version comparison.

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
    mcp.run()


if __name__ == "__main__":
    main()
