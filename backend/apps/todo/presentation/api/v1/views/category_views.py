"""Category API views."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from dataclasses import asdict

from apps.todo.application.use_cases.category_use_cases import (
    CreateCategoryUseCase,
    ListCategoriesUseCase,
    UpdateCategoryUseCase,
    DeleteCategoryUseCase
)
from apps.todo.application.dto.category_dto import CreateCategoryDTO, UpdateCategoryDTO
from apps.todo.infrastructure.persistence.repositories.category_repository_impl import CategoryRepository
from apps.todo.presentation.api.v1.serializers.category_serializers import (
    CategorySerializer,
    CreateCategorySerializer,
    UpdateCategorySerializer
)
from apps.todo.domain.exceptions.exceptions import CategoryNotFoundException


class CategoryListCreateView(APIView):
    """List and create categories."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """List all categories."""
        try:
            category_repo = CategoryRepository()
            use_case = ListCategoriesUseCase(category_repo)

            categories = use_case.execute()
            serializer = CategorySerializer([asdict(c) for c in categories], many=True)

            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Create a new category."""
        try:
            serializer = CreateCategorySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            category_repo = CategoryRepository()
            use_case = CreateCategoryUseCase(category_repo)

            dto = CreateCategoryDTO(**serializer.validated_data)
            category = use_case.execute(dto)

            response_serializer = CategorySerializer(asdict(category))
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CategoryDetailView(APIView):
    """Retrieve, update, and delete a category."""

    permission_classes = [IsAuthenticated]

    def get(self, request, category_id):
        """Get category by ID."""
        try:
            category_repo = CategoryRepository()
            category = category_repo.get_by_id(category_id)

            if not category:
                return Response(
                    {"error": "Category not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = CategorySerializer(asdict(category))
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request, category_id):
        """Update category."""
        try:
            serializer = UpdateCategorySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            category_repo = CategoryRepository()
            use_case = UpdateCategoryUseCase(category_repo)

            dto = UpdateCategoryDTO(
                category_id=category_id,
                **serializer.validated_data
            )

            category = use_case.execute(dto)
            response_serializer = CategorySerializer(asdict(category))

            return Response(response_serializer.data)

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

    def delete(self, request, category_id):
        """Delete category."""
        try:
            category_repo = CategoryRepository()
            use_case = DeleteCategoryUseCase(category_repo)

            success = use_case.execute(category_id)

            if success:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"error": "Failed to delete category"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
