from datetime import datetime, timezone, timedelta

ADAK_TZ = timezone(timedelta(hours=-10))
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from infrastructure.api_client.backend_client import BackendAPIClient

router = Router()


@router.message(Command("list"))
async def cmd_list_tasks(message: Message):
    """Показать список задач пользователя."""
    try:
        async with BackendAPIClient(telegram_user_id=message.from_user.id) as client:
            tasks = await client.get_tasks()

        if not tasks:
            await message.answer(
                "У вас пока нет задач.\n\nИспользуйте /create, чтобы добавить первую задачу."
            )
            return

        text = "Ваши задачи:\n\n"
        for i, task in enumerate(tasks, 1):
            status = "[выполнена]" if task.is_completed else "[в работе]"
            category_info = f" [{task.category_name}]" if task.category_name else ""

            created_date = datetime.fromisoformat(task.created_at.replace("Z", "+00:00"))
            date_str = created_date.astimezone(ADAK_TZ).strftime("%d.%m.%Y %H:%M")

            text += (
                f"{i}. {status} <b>{task.title}</b>{category_info}\n"
                f"   {task.description}\n"
                f"   Создана: {date_str}\n"
            )

            if task.due_date:
                due_date = datetime.fromisoformat(task.due_date.replace("Z", "+00:00"))
                due_str = due_date.astimezone(ADAK_TZ).strftime("%d.%m.%Y %H:%M")
                text += f"   Срок: {due_str} (Adak)\n"

            text += "\n"

        await message.answer(text, parse_mode="HTML")

    except Exception as e:
        await message.answer(f"Ошибка при загрузке задач: {str(e)}")


@router.message(Command("categories"))
async def cmd_list_categories(message: Message):
    """Показать список категорий."""
    try:
        async with BackendAPIClient(telegram_user_id=message.from_user.id) as client:
            categories = await client.get_categories()

        if not categories:
            await message.answer(
                "Категорий пока нет.\n\n"
                "Создайте категорию через Django Admin: http://localhost:8000/admin/"
            )
            return

        text = "Категории:\n\n"
        for i, cat in enumerate(categories, 1):
            text += f"{i}. <b>{cat.name}</b>\n   {cat.description}\n\n"

        await message.answer(text, parse_mode="HTML")

    except Exception as e:
        await message.answer(f"Ошибка при загрузке категорий: {str(e)}")
