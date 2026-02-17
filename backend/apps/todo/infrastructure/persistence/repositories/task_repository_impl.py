from typing import List, Optional
from datetime import datetime

from django.utils import timezone

from apps.todo.application.interfaces.task_repository import ITaskRepository
from apps.todo.domain.entities.task import Task as TaskEntity
from apps.todo.infrastructure.persistence.models import Task as TaskModel


class TaskRepository(ITaskRepository):
    """Django ORM implementation of task repository."""

    def _to_entity(self, model: TaskModel) -> TaskEntity:
        """Convert Django model to domain entity."""
        return TaskEntity(
            id=model.id,
            title=model.title,
            description=model.description,
            user_id=model.user_id,
            category_id=model.category_id,
            due_date=model.due_date,
            is_completed=model.is_completed,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _to_model(self, entity: TaskEntity, model: Optional[TaskModel] = None) -> TaskModel:
        """Convert domain entity to Django model."""
        if model is None:
            model = TaskModel()

        model.id = entity.id
        model.title = entity.title
        model.description = entity.description
        model.user_id = entity.user_id
        model.category_id = entity.category_id
        model.due_date = entity.due_date
        model.is_completed = entity.is_completed

        return model

    def create(self, task: TaskEntity) -> TaskEntity:
        """Create a new task."""
        model = self._to_model(task)
        model.save()
        return self._to_entity(model)

    def get_by_id(self, task_id: str) -> Optional[TaskEntity]:
        """Get task by ID."""
        try:
            model = TaskModel.objects.get(id=task_id)
            return self._to_entity(model)
        except TaskModel.DoesNotExist:
            return None

    def get_by_user_id(self, user_id: int) -> List[TaskEntity]:
        """Get all tasks for a user."""
        models = TaskModel.objects.filter(user_id=user_id)
        return [self._to_entity(m) for m in models]

    def get_by_category(self, category_id: str) -> List[TaskEntity]:
        """Get all tasks in a category."""
        models = TaskModel.objects.filter(category_id=category_id)
        return [self._to_entity(m) for m in models]

    def get_overdue_tasks(self) -> List[TaskEntity]:
        """Get all overdue tasks."""
        now = timezone.now()
        models = TaskModel.objects.filter(
            due_date__lt=now,
            is_completed=False
        )
        return [self._to_entity(m) for m in models]

    def update(self, task: TaskEntity) -> TaskEntity:
        """Update a task."""
        model = TaskModel.objects.get(id=task.id)
        model = self._to_model(task, model)
        model.save()
        return self._to_entity(model)

    def delete(self, task_id: str) -> bool:
        """Delete a task."""
        try:
            TaskModel.objects.get(id=task_id).delete()
            return True
        except TaskModel.DoesNotExist:
            return False
