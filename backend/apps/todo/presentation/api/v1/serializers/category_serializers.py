from rest_framework import serializers


class CategorySerializer(serializers.Serializer):
    """Category serializer."""

    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=100)
    description = serializers.CharField()
    color = serializers.CharField(max_length=7)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class CreateCategorySerializer(serializers.Serializer):
    """Create category serializer."""

    name = serializers.CharField(max_length=100)
    description = serializers.CharField()
    color = serializers.CharField(max_length=7, default="#3B82F6")


class UpdateCategorySerializer(serializers.Serializer):
    """Update category serializer."""

    name = serializers.CharField(max_length=100, required=False)
    description = serializers.CharField(required=False)
    color = serializers.CharField(max_length=7, required=False)
