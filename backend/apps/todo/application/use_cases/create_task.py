from datetime import datetime

from apps.todo.domain.entities.task import Task
from apps.todo.domain.value_objects.task_id import ULIDGenerator
from apps.todo.application.interfaces.task_repository import ITaskRepository
from apps.todo.application.interfaces.category_repository import ICategoryRepository
from apps.todo.application.dto.task_dto import CreateTaskDTO, TaskDTO
from apps.todo.domain.exceptions.exceptions import CategoryNotFoundException


class CreateTaskUseCase:
    """Use case for creating a new task."""

    def __init__(
        self,
        task_repository: ITaskRepository,
        category_repository: ICategoryRepository
    ):
        self.task_repository = task_repository
        self.category_repository = category_repository

    def execute(self, dto: CreateTaskDTO) -> TaskDTO:
        """Execute the use case."""
        if dto.category_id:
            category = self.category_repository.get_by_id(dto.category_id)
            if not category:
                raise CategoryNotFoundException(dto.category_id)

        now = datetime.now()
        task = Task(
            id=ULIDGenerator.generate(),
            title=dto.title,
            description=dto.description,
            user_id=dto.user_id,
            category_id=dto.category_id,
            due_date=dto.due_date,
            is_completed=False,
            created_at=now,
            updated_at=now
        )

        created_task = self.task_repository.create(task)

        category_name = None
        if created_task.category_id:
            category = self.category_repository.get_by_id(created_task.category_id)
            category_name = category.name if category else None

        return TaskDTO(
            id=created_task.id,
            title=created_task.title,
            description=created_task.description,
            user_id=created_task.user_id,
            category_id=created_task.category_id,
            category_name=category_name,
            due_date=created_task.due_date,
            is_completed=created_task.is_completed,
            created_at=created_task.created_at,
            updated_at=created_task.updated_at
        )
