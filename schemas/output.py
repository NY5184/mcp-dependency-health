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
    repository_url: Optional[str] = None  # Link to source code repository
    homepage_url: Optional[str] = None  # Project homepage
    changelog_url: Optional[str] = None  # Link to changelog/release notes
    description: Optional[str] = None  # Short package description


class DependencyHealthOutput(BaseModel):
    dependencies: List[DependencyResult]
