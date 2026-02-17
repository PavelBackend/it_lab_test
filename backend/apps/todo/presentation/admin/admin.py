from django import forms
from django.contrib import admin

from apps.todo.domain.value_objects.task_id import ULIDGenerator
from apps.todo.infrastructure.persistence.models import Task, Category, UserProfile


class CategoryAdminForm(forms.ModelForm):
    """Форма для Category — гарантирует генерацию ULID до валидации."""

    class Meta:
        model = Category
        fields = ["name", "description", "color"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.instance.id = ULIDGenerator.generate()


class TaskAdminForm(forms.ModelForm):
    """Форма для Task — гарантирует генерацию ULID до валидации."""

    class Meta:
        model = Task
        fields = ["title", "description", "user", "category", "due_date", "is_completed"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.instance.id = ULIDGenerator.generate()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm

    list_display = ["id", "name", "color", "created_at"]
    search_fields = ["name", "description"]
    list_filter = ["created_at"]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["id", "created_at", "updated_at"]
        return ["created_at", "updated_at"]

    def get_fieldsets(self, request, obj=None):
        if obj:
            return (
                ("Основная информация", {"fields": ("id", "name", "description", "color")}),
                ("Даты", {"fields": ("created_at", "updated_at")}),
            )
        return (
            ("Основная информация", {"fields": ("name", "description", "color")}),
        )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    form = TaskAdminForm

    list_display = ["id", "title", "user", "category", "due_date", "is_completed", "created_at"]
    search_fields = ["title", "description", "user__username"]
    list_filter = ["is_completed", "category", "due_date", "created_at"]
    date_hierarchy = "due_date"

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["id", "created_at", "updated_at"]
        return ["created_at", "updated_at"]

    def get_fieldsets(self, request, obj=None):
        base = [
            ("Основная информация", {"fields": ("title", "description", "user")}),
            ("Категория", {"fields": ("category",)}),
            ("Статус", {"fields": ("is_completed", "due_date")}),
        ]
        if obj:
            base.insert(0, ("ID", {"fields": ("id",)}))
            base.append(("Даты", {"fields": ("created_at", "updated_at")}))
        return base


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "telegram_id"]
    search_fields = ["user__username"]
    readonly_fields = ["user"]
