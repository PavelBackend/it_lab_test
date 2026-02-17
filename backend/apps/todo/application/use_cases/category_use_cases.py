from datetime import datetime
from typing import List

from apps.todo.domain.entities.category import Category
from apps.todo.domain.value_objects.task_id import ULIDGenerator
from apps.todo.application.interfaces.category_repository import ICategoryRepository
from apps.todo.application.dto.category_dto import (
    CreateCategoryDTO,
    UpdateCategoryDTO,
    CategoryDTO
)
from apps.todo.domain.exceptions.exceptions import CategoryNotFoundException


class CreateCategoryUseCase:
    """Use case for creating a category."""

    def __init__(self, category_repository: ICategoryRepository):
        self.category_repository = category_repository

    def execute(self, dto: CreateCategoryDTO) -> CategoryDTO:
        """Execute the use case."""
        now = datetime.now()
        category = Category(
            id=ULIDGenerator.generate(),
            name=dto.name,
            description=dto.description,
            color=dto.color,
            created_at=now,
            updated_at=now
        )

        created = self.category_repository.create(category)

        return CategoryDTO(
            id=created.id,
            name=created.name,
            description=created.description,
            color=created.color,
            created_at=created.created_at,
            updated_at=created.updated_at
        )


class ListCategoriesUseCase:
    """Use case for listing categories."""

    def __init__(self, category_repository: ICategoryRepository):
        self.category_repository = category_repository

    def execute(self) -> List[CategoryDTO]:
        """Execute the use case."""
        categories = self.category_repository.get_all()

        return [
            CategoryDTO(
                id=cat.id,
                name=cat.name,
                description=cat.description,
                color=cat.color,
                created_at=cat.created_at,
                updated_at=cat.updated_at
            )
            for cat in categories
        ]


class UpdateCategoryUseCase:
    """Use case for updating a category."""

    def __init__(self, category_repository: ICategoryRepository):
        self.category_repository = category_repository

    def execute(self, dto: UpdateCategoryDTO) -> CategoryDTO:
        """Execute the use case."""
        category = self.category_repository.get_by_id(dto.category_id)
        if not category:
            raise CategoryNotFoundException(dto.category_id)

        if dto.name is not None:
            category.name = dto.name
        if dto.description is not None:
            category.description = dto.description
        if dto.color is not None:
            category.color = dto.color

        category.updated_at = datetime.now()

        updated = self.category_repository.update(category)

        return CategoryDTO(
            id=updated.id,
            name=updated.name,
            description=updated.description,
            color=updated.color,
            created_at=updated.created_at,
            updated_at=updated.updated_at
        )


class DeleteCategoryUseCase:
    """Use case for deleting a category."""

    def __init__(self, category_repository: ICategoryRepository):
        self.category_repository = category_repository

    def execute(self, category_id: str) -> bool:
        """Execute the use case."""
        category = self.category_repository.get_by_id(category_id)
        if not category:
            raise CategoryNotFoundException(category_id)

        return self.category_repository.delete(category_id)
