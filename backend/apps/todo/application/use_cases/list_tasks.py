from typing import List, Optional

from apps.todo.application.interfaces.task_repository import ITaskRepository
from apps.todo.application.interfaces.category_repository import ICategoryRepository
from apps.todo.application.dto.task_dto import TaskDTO


class ListTasksUseCase:
    """Use case for listing tasks."""

    def __init__(
        self,
        task_repository: ITaskRepository,
        category_repository: ICategoryRepository
    ):
        self.task_repository = task_repository
        self.category_repository = category_repository

    def execute(self, user_id: int, category_id: Optional[str] = None) -> List[TaskDTO]:
        """Execute the use case."""
        if category_id:
            tasks = self.task_repository.get_by_category(category_id)
            tasks = [t for t in tasks if t.user_id == user_id]
        else:
            tasks = self.task_repository.get_by_user_id(user_id)

        result = []
        for task in tasks:
            category_name = None
            if task.category_id:
                category = self.category_repository.get_by_id(task.category_id)
                category_name = category.name if category else None

            result.append(TaskDTO(
                id=task.id,
                title=task.title,
                description=task.description,
                user_id=task.user_id,
                category_id=task.category_id,
                category_name=category_name,
                due_date=task.due_date,
                is_completed=task.is_completed,
                created_at=task.created_at,
                updated_at=task.updated_at
            ))

        return result
