from __future__ import annotations
from pathlib import Path
from typing import Optional


def find_dependency_files(project_path: str) -> dict[str, Optional[Path]]:
    """
    Locates dependency manifest files in the specified project directory.
    
    Returns a dictionary with keys 'package_json' and 'requirements_txt', containing
    Path objects if the files exist, or None if they don't.
    """
    root = Path(project_path).resolve()

    package_json = root / "package.json"
    requirements_txt = root / "requirements.txt"

    return {
        "package_json": package_json if package_json.exists() else None,
        "requirements_txt": requirements_txt if requirements_txt.exists() else None,
    }
