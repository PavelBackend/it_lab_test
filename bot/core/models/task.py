from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """Task model."""
    id: str
    title: str
    description: str
    user_id: int
    category_id: Optional[str]
    category_name: Optional[str]
    due_date: Optional[str]
    is_completed: bool
    created_at: str
    updated_at: str


@dataclass
class Category:
    """Category model."""
    id: str
    name: str
    description: str
    color: str
    created_at: str
    updated_at: str
