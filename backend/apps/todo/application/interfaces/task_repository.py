from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from apps.todo.domain.entities.task import Task


class ITaskRepository(ABC):
    """Interface for task repository."""

    @abstractmethod
    def create(self, task: Task) -> Task:
        """Create a new task."""
        pass

    @abstractmethod
    def get_by_id(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> List[Task]:
        """Get all tasks for a user."""
        pass

    @abstractmethod
    def get_by_category(self, category_id: str) -> List[Task]:
        """Get all tasks in a category."""
        pass

    @abstractmethod
    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks."""
        pass

    @abstractmethod
    def update(self, task: Task) -> Task:
        """Update a task."""
        pass

    @abstractmethod
    def delete(self, task_id: str) -> bool:
        """Delete a task."""
        pass
