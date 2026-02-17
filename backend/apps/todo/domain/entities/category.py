from dataclasses import dataclass
from datetime import datetime


@dataclass
class Category:
    """Category entity for organizing tasks."""

    id: str
    name: str
    description: str
    color: str  # Hex код цвета
    created_at: datetime
    updated_at: datetime

    def update_name(self, new_name: str) -> None:
        """Update category name."""
        self.name = new_name
        self.updated_at = datetime.now()
