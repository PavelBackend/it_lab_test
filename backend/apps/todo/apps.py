from django.apps import AppConfig


class TodoConfig(AppConfig):
    """Configuration for todo app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.todo'
    verbose_name = 'Todo Application'

    def ready(self):
        """Import models and tasks when app is ready."""
        from apps.todo.infrastructure.persistence import models
        from apps.todo.presentation.admin import admin
