from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Tuple


def parse_package_json(path: Path) -> Dict[str, str]:
    """
    Parses a package.json file and extracts all dependencies from all dependency sections.
    
    Returns a dictionary mapping package names to their version specifiers (e.g., "^1.2.3").
    Includes dependencies, devDependencies, peerDependencies, and optionalDependencies.
    """
    data = json.loads(path.read_text(encoding="utf-8"))

    deps: Dict[str, str] = {}
    for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        block = data.get(section) or {}
        if isinstance(block, dict):
            for name, ver in block.items():
                if isinstance(name, str) and isinstance(ver, str):
                    deps[name] = ver.strip()
    return deps


def parse_requirements_txt(path: Path) -> List[Tuple[str, str]]:
    """
    Parses a requirements.txt file and extracts package names with their version specifiers.
    
    Returns a list of tuples (name, spec_string) where spec_string is the version constraint
    that appears after the name (e.g., "==1.2.3" or ">=2.0"). Skips comments, editable installs,
    nested requirement files, and handles VCS/URL dependencies.
    """
    out: List[Tuple[str, str]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-r") or line.startswith("--requirement"):
            # keep it simple for now: skip nested files
            continue
        if line.startswith("-e") or line.startswith("--editable"):
            continue
        if "@" in line and "://" in line:
            # VCS/URL dependency
            name = line.split("@", 1)[0].strip()
            out.append((name or line, line))
            continue

        # split like: package==1.2.3 / package>=1.0 / package
        name = ""
        spec = ""
        for sep in ["==", ">=", "<=", "~=", "!=", ">", "<"]:
            if sep in line:
                left, right = line.split(sep, 1)
                name = left.strip()
                spec = sep + right.strip()
                break
        if not name:
            name = line.strip()
            spec = ""
        out.append((name, spec))
    return out
