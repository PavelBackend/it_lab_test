from abc import ABC, abstractmethod
from typing import List, Optional

from apps.todo.domain.entities.category import Category


class ICategoryRepository(ABC):
    """Interface for category repository."""

    @abstractmethod
    def create(self, category: Category) -> Category:
        """Create a new category."""
        pass

    @abstractmethod
    def get_by_id(self, category_id: str) -> Optional[Category]:
        """Get category by ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[Category]:
        """Get all categories."""
        pass

    @abstractmethod
    def update(self, category: Category) -> Category:
        """Update a category."""
        pass

    @abstractmethod
    def delete(self, category_id: str) -> bool:
        """Delete a category."""
        pass
