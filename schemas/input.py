from enum import Enum
from pathlib import Path
from pydantic import BaseModel, field_validator, ValidationError


class Ecosystem(str, Enum):
    auto = "auto"          # detect by files
    javascript = "javascript"
    python = "python"


class DependencyHealthInput(BaseModel):
    project_path: str
    ecosystem: Ecosystem = Ecosystem.auto

    @field_validator("project_path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """
        Validate and normalize the project path.
        
        Ensures the path:
        - Exists on the filesystem
        - Is a directory (not a file)
        - Is resolved to an absolute path (prevents path traversal)
        
        Raises:
            ValueError: If path is invalid, doesn't exist, or isn't a directory
        """
        # Strip whitespace and quotes
        v = v.strip().strip('"').strip("'")
        
        if not v:
            raise ValueError("project_path cannot be empty")
        
        # Convert to Path object and resolve to absolute path
        # This also normalizes the path and resolves symlinks
        try:
            path = Path(v).resolve()
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Invalid path: {e}")
        
        # Check if path exists
        if not path.exists():
            raise ValueError(f"Path does not exist: {v}")
        
        # Check if it's a directory
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {v}")
        
        # Return the resolved absolute path as a string
        return str(path)
