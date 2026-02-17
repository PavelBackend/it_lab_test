from apps.todo.application.interfaces.task_repository import ITaskRepository
from apps.todo.domain.exceptions.exceptions import (
    TaskNotFoundException,
    UnauthorizedAccessException
)


class DeleteTaskUseCase:
    """Use case for deleting a task."""

    def __init__(self, task_repository: ITaskRepository):
        self.task_repository = task_repository

    def execute(self, task_id: str, user_id: int) -> bool:
        """Execute the use case."""
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise TaskNotFoundException(task_id)

        if task.user_id != user_id:
            raise UnauthorizedAccessException("You can only delete your own tasks")

        return self.task_repository.delete(task_id)
