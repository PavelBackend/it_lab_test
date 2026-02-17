from typing import List, Optional

from apps.todo.application.interfaces.category_repository import ICategoryRepository
from apps.todo.domain.entities.category import Category as CategoryEntity
from apps.todo.infrastructure.persistence.models import Category as CategoryModel


class CategoryRepository(ICategoryRepository):
    """Django ORM implementation of category repository."""

    def _to_entity(self, model: CategoryModel) -> CategoryEntity:
        """Convert Django model to domain entity."""
        return CategoryEntity(
            id=model.id,
            name=model.name,
            description=model.description,
            color=model.color,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _to_model(self, entity: CategoryEntity, model: Optional[CategoryModel] = None) -> CategoryModel:
        """Convert domain entity to Django model."""
        if model is None:
            model = CategoryModel()

        model.id = entity.id
        model.name = entity.name
        model.description = entity.description
        model.color = entity.color

        return model

    def create(self, category: CategoryEntity) -> CategoryEntity:
        """Create a new category."""
        model = self._to_model(category)
        model.save()
        return self._to_entity(model)

    def get_by_id(self, category_id: str) -> Optional[CategoryEntity]:
        """Get category by ID."""
        try:
            model = CategoryModel.objects.get(id=category_id)
            return self._to_entity(model)
        except CategoryModel.DoesNotExist:
            return None

    def get_all(self) -> List[CategoryEntity]:
        """Get all categories."""
        models = CategoryModel.objects.all()
        return [self._to_entity(m) for m in models]

    def update(self, category: CategoryEntity) -> CategoryEntity:
        """Update a category."""
        model = CategoryModel.objects.get(id=category.id)
        model = self._to_model(category, model)
        model.save()
        return self._to_entity(model)

    def delete(self, category_id: str) -> bool:
        """Delete a category."""
        try:
            CategoryModel.objects.get(id=category_id).delete()
            return True
        except CategoryModel.DoesNotExist:
            return False
