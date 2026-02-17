"""Task API views."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from dataclasses import asdict

from apps.todo.application.use_cases.create_task import CreateTaskUseCase
from apps.todo.application.use_cases.list_tasks import ListTasksUseCase
from apps.todo.application.use_cases.update_task import UpdateTaskUseCase
from apps.todo.application.use_cases.delete_task import DeleteTaskUseCase
from apps.todo.application.dto.task_dto import CreateTaskDTO, UpdateTaskDTO
from apps.todo.infrastructure.persistence.repositories.task_repository_impl import TaskRepository
from apps.todo.infrastructure.persistence.repositories.category_repository_impl import CategoryRepository
from apps.todo.infrastructure.persistence.models import Task as TaskModel
from apps.todo.presentation.api.v1.serializers.task_serializers import (
    TaskSerializer,
    CreateTaskSerializer,
    UpdateTaskSerializer
)
from apps.todo.domain.exceptions.exceptions import (
    TaskNotFoundException,
    CategoryNotFoundException,
    UnauthorizedAccessException
)


def _schedule_notification(task_id: str, due_date_str) -> str | None:
    """Планирует Celery-таск на точное время срока задачи. Возвращает celery_task_id."""
    if not due_date_str:
        return None
    try:
        from datetime import datetime
        from apps.todo.infrastructure.tasks.notifications import notify_task_due

        due_dt = datetime.fromisoformat(str(due_date_str))
        result = notify_task_due.apply_async(args=[task_id], eta=due_dt)
        return result.id
    except Exception as e:
        print(f"[schedule] Ошибка планирования уведомления для задачи {task_id}: {e}")
        return None


def _revoke_notification(celery_task_id: str) -> None:
    """Отменяет запланированный Celery-таск."""
    if not celery_task_id:
        return
    try:
        from config.celery import app as celery_app
        celery_app.control.revoke(celery_task_id, terminate=True)
    except Exception as e:
        print(f"[revoke] Ошибка отмены Celery-таска {celery_task_id}: {e}")


class TaskListCreateView(APIView):
    """List and create tasks."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """List tasks for current user."""
        try:
            task_repo = TaskRepository()
            category_repo = CategoryRepository()
            use_case = ListTasksUseCase(task_repo, category_repo)

            category_id = request.query_params.get('category_id')
            tasks = use_case.execute(request.user.id, category_id)

            serializer = TaskSerializer([asdict(t) for t in tasks], many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Create a new task."""
        try:
            serializer = CreateTaskSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            task_repo = TaskRepository()
            category_repo = CategoryRepository()
            use_case = CreateTaskUseCase(task_repo, category_repo)

            dto = CreateTaskDTO(
                title=serializer.validated_data['title'],
                description=serializer.validated_data['description'],
                user_id=request.user.id,
                category_id=serializer.validated_data.get('category_id'),
                due_date=serializer.validated_data.get('due_date')
            )

            task = use_case.execute(dto)

            # Планируем точное уведомление на срок задачи
            if task.due_date:
                celery_task_id = _schedule_notification(task.id, task.due_date)
                if celery_task_id:
                    TaskModel.objects.filter(id=task.id).update(celery_task_id=celery_task_id)

            response_serializer = TaskSerializer(asdict(task))
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        except CategoryNotFoundException as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TaskDetailView(APIView):
    """Retrieve, update, and delete a task."""

    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        """Get task by ID."""
        try:
            task_repo = TaskRepository()
            task = task_repo.get_by_id(task_id)

            if not task:
                return Response(
                    {"error": "Task not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            if task.user_id != request.user.id:
                return Response(
                    {"error": "Unauthorized"},
                    status=status.HTTP_403_FORBIDDEN
                )

            category_name = None
            if task.category_id:
                category_repo = CategoryRepository()
                category = category_repo.get_by_id(task.category_id)
                category_name = category.name if category else None

            task_dict = asdict(task)
            task_dict['category_name'] = category_name

            serializer = TaskSerializer(task_dict)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request, task_id):
        """Update task."""
        try:
            serializer = UpdateTaskSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Отменяем старое уведомление перед обновлением
            existing = TaskModel.objects.filter(id=task_id).values_list(
                'celery_task_id', flat=True
            ).first()
            _revoke_notification(existing)

            task_repo = TaskRepository()
            category_repo = CategoryRepository()
            use_case = UpdateTaskUseCase(task_repo, category_repo)

            dto = UpdateTaskDTO(
                task_id=task_id,
                **serializer.validated_data
            )

            task = use_case.execute(dto, request.user.id)

            # Планируем новое уведомление если есть срок и задача не выполнена
            new_celery_id = None
            if task.due_date and not task.is_completed:
                new_celery_id = _schedule_notification(task.id, task.due_date)
            TaskModel.objects.filter(id=task.id).update(celery_task_id=new_celery_id)

            response_serializer = TaskSerializer(asdict(task))
            return Response(response_serializer.data)

        except TaskNotFoundException as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except (CategoryNotFoundException, UnauthorizedAccessException) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, task_id):
        """Delete task."""
        try:
            # Отменяем уведомление перед удалением
            existing = TaskModel.objects.filter(id=task_id).values_list(
                'celery_task_id', flat=True
            ).first()
            _revoke_notification(existing)

            task_repo = TaskRepository()
            use_case = DeleteTaskUseCase(task_repo)

            success = use_case.execute(task_id, request.user.id)

            if success:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"error": "Failed to delete task"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except TaskNotFoundException as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except UnauthorizedAccessException as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
