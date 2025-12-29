from typing import List, Optional
from pydantic import BaseModel


class DependencyResult(BaseModel):
    name: str
    current: str
    latest: str
    status: str  # "outdated" | "up-to-date" | "unknown"
    note: Optional[str] = None


class DependencyHealthOutput(BaseModel):
    dependencies: List[DependencyResult]
