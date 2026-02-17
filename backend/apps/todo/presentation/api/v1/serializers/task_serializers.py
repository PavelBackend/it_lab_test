from rest_framework import serializers
from django.contrib.auth.models import User


class TaskSerializer(serializers.Serializer):
    """Task serializer."""

    id = serializers.CharField(read_only=True)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField()
    user_id = serializers.IntegerField(read_only=True)
    category_id = serializers.CharField(required=False, allow_null=True)
    category_name = serializers.CharField(read_only=True, required=False)
    due_date = serializers.DateTimeField(required=False, allow_null=True)
    is_completed = serializers.BooleanField(default=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class CreateTaskSerializer(serializers.Serializer):
    """Create task serializer."""

    title = serializers.CharField(max_length=200)
    description = serializers.CharField()
    category_id = serializers.CharField(required=False, allow_null=True)
    due_date = serializers.DateTimeField(required=False, allow_null=True)


class UpdateTaskSerializer(serializers.Serializer):
    """Update task serializer."""

    title = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(required=False)
    category_id = serializers.CharField(required=False, allow_null=True)
    due_date = serializers.DateTimeField(required=False, allow_null=True)
    is_completed = serializers.BooleanField(required=False)
