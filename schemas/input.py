from enum import Enum
from pydantic import BaseModel, field_validator


class Ecosystem(str, Enum):
    auto = "auto"          # detect by files
    javascript = "javascript"
    python = "python"


class DependencyHealthInput(BaseModel):
    project_path: str
    ecosystem: Ecosystem = Ecosystem.auto

    @field_validator("project_path")
    @classmethod
    def normalize_path(cls, v: str) -> str:
        v = v.strip().strip('"').strip("'")
        return v
