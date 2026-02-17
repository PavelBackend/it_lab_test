from django.db import models
from django.contrib.auth.models import User

from apps.todo.domain.value_objects.task_id import ULIDGenerator


class Category(models.Model):
    """Category model."""

    id = models.CharField(max_length=26, primary_key=True, default=ULIDGenerator.generate, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#3B82F6")  # Hex код цвета
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categories"
        verbose_name_plural = "Categories"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = ULIDGenerator.generate()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Task(models.Model):
    """Task model."""

    id = models.CharField(max_length=26, primary_key=True, default=ULIDGenerator.generate, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks"
    )
    due_date = models.DateTimeField(null=True, blank=True)
    celery_task_id = models.CharField(max_length=64, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tasks"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["category"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["is_completed"]),
        ]

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = ULIDGenerator.generate()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    """Профиль пользователя с Telegram ID для уведомлений."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)

    class Meta:
        db_table = "user_profiles"

    def __str__(self):
        return f"{self.user.username} (tg: {self.telegram_id})"
