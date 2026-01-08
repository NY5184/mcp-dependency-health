from typing import List, Optional
from pydantic import BaseModel


class DependencyResult(BaseModel):
    name: str
    current: str
    latest: str
    status: str  # "outdated" | "up-to-date" | "unknown"
    note: Optional[str] = None
    # Enhanced context for LLM upgrade analysis
    release_date: Optional[str] = None  # When the latest version was released
    changelog_content: str  # Release notes or explanation text (always present)
    description: Optional[str] = None  # Short package description


class DependencyHealthOutput(BaseModel):
    dependencies: List[DependencyResult]
