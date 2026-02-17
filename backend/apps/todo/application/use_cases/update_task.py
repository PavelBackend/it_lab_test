from datetime import datetime

from apps.todo.application.interfaces.task_repository import ITaskRepository
from apps.todo.application.interfaces.category_repository import ICategoryRepository
from apps.todo.application.dto.task_dto import UpdateTaskDTO, TaskDTO
from apps.todo.domain.exceptions.exceptions import (
    TaskNotFoundException,
    CategoryNotFoundException,
    UnauthorizedAccessException
)


class UpdateTaskUseCase:
    """Use case for updating a task."""

    def __init__(
        self,
        task_repository: ITaskRepository,
        category_repository: ICategoryRepository
    ):
        self.task_repository = task_repository
        self.category_repository = category_repository

    def execute(self, dto: UpdateTaskDTO, user_id: int) -> TaskDTO:
        """Execute the use case."""
        task = self.task_repository.get_by_id(dto.task_id)
        if not task:
            raise TaskNotFoundException(dto.task_id)

        if task.user_id != user_id:
            raise UnauthorizedAccessException("You can only update your own tasks")

        if dto.category_id:
            category = self.category_repository.get_by_id(dto.category_id)
            if not category:
                raise CategoryNotFoundException(dto.category_id)

        if dto.title is not None:
            task.title = dto.title
        if dto.description is not None:
            task.description = dto.description
        if dto.category_id is not None:
            task.category_id = dto.category_id
        if dto.due_date is not None:
            task.due_date = dto.due_date
        if dto.is_completed is not None:
            task.is_completed = dto.is_completed

        task.updated_at = datetime.now()

        updated_task = self.task_repository.update(task)

        category_name = None
        if updated_task.category_id:
            category = self.category_repository.get_by_id(updated_task.category_id)
            category_name = category.name if category else None

        return TaskDTO(
            id=updated_task.id,
            title=updated_task.title,
            description=updated_task.description,
            user_id=updated_task.user_id,
            category_id=updated_task.category_id,
            category_name=category_name,
            due_date=updated_task.due_date,
            is_completed=updated_task.is_completed,
            created_at=updated_task.created_at,
            updated_at=updated_task.updated_at
        )
