from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CreateTaskDTO:
    """DTO for creating a task."""
    title: str
    description: str
    user_id: int
    category_id: Optional[str] = None
    due_date: Optional[datetime] = None


@dataclass
class UpdateTaskDTO:
    """DTO for updating a task."""
    task_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    due_date: Optional[datetime] = None
    is_completed: Optional[bool] = None


@dataclass
class TaskDTO:
    """DTO for returning task data."""
    id: str
    title: str
    description: str
    user_id: int
    category_id: Optional[str]
    category_name: Optional[str]
    due_date: Optional[datetime]
    is_completed: bool
    created_at: datetime
    updated_at: datetime
