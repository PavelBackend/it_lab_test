import httpx
from typing import List, Optional, Dict, Any
from decouple import config

from core.models.task import Task, Category


class BackendAPIClient:
    """Client for Django backend API."""

    def __init__(self, telegram_user_id: Optional[int] = None):
        self.base_url = config('BACKEND_API_URL', default='http://localhost:8000')
        self.username = config('BACKEND_USERNAME', default='')
        self.password = config('BACKEND_PASSWORD', default='')
        self.telegram_user_id = telegram_user_id
        self.session: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Context manager entry."""
        headers = {}
        if self.telegram_user_id:
            headers["X-Telegram-User-Id"] = str(self.telegram_user_id)

        self.session = httpx.AsyncClient(
            base_url=self.base_url,
            auth=(self.username, self.password) if self.username else None,
            headers=headers,
            timeout=30.0
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.session:
            await self.session.aclose()

    async def get_tasks(self, category_id: Optional[str] = None) -> List[Task]:
        """Get tasks list."""
        params = {}
        if category_id:
            params['category_id'] = category_id

        response = await self.session.get('/api/v1/tasks/', params=params)
        response.raise_for_status()

        tasks_data = response.json()
        return [Task(**task) for task in tasks_data]

    async def create_task(
        self,
        title: str,
        description: str,
        category_id: Optional[str] = None,
        due_date: Optional[str] = None
    ) -> Task:
        """Create a new task."""
        data = {
            'title': title,
            'description': description,
        }
        if category_id:
            data['category_id'] = category_id
        if due_date:
            data['due_date'] = due_date

        response = await self.session.post('/api/v1/tasks/', json=data)
        response.raise_for_status()

        task_data = response.json()
        return Task(**task_data)

    async def get_categories(self) -> List[Category]:
        """Get categories list."""
        response = await self.session.get('/api/v1/categories/')
        response.raise_for_status()

        categories_data = response.json()
        return [Category(**cat) for cat in categories_data]

    async def get_task(self, task_id: str) -> Task:
        """Get task by ID."""
        response = await self.session.get(f'/api/v1/tasks/{task_id}/')
        response.raise_for_status()

        task_data = response.json()
        return Task(**task_data)
