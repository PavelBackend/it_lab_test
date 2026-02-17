from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CreateCategoryDTO:
    """DTO for creating a category."""
    name: str
    description: str
    color: str = "#3B82F6"


@dataclass
class UpdateCategoryDTO:
    """DTO for updating a category."""
    category_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None


@dataclass
class CategoryDTO:
    """DTO for returning category data."""
    id: str
    name: str
    description: str
    color: str
    created_at: datetime
    updated_at: datetime
