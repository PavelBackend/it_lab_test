"""API v1 URLs."""
from django.urls import path

from apps.todo.presentation.api.v1.views.task_views import (
    TaskListCreateView,
    TaskDetailView
)
from apps.todo.presentation.api.v1.views.category_views import (
    CategoryListCreateView,
    CategoryDetailView
)

urlpatterns = [
    # Tasks
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<str:task_id>/', TaskDetailView.as_view(), name='task-detail'),

    # Categories
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<str:category_id>/', CategoryDetailView.as_view(), name='category-detail'),
]
