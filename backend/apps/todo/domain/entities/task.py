from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """Task entity representing a todo item."""

    id: str
    title: str
    description: str
    user_id: int
    category_id: Optional[str]
    due_date: Optional[datetime]
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    def mark_as_completed(self) -> None:
        """Mark task as completed."""
        self.is_completed = True
        self.updated_at = datetime.now()

    def update_due_date(self, new_date: datetime) -> None:
        """Update task due date."""
        self.due_date = new_date
        self.updated_at = datetime.now()

    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if not self.due_date or self.is_completed:
            return False
        return datetime.now() > self.due_date
