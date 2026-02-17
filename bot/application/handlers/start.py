from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработать команду /start."""
    await message.answer(
        "Привет! Это бот для управления задачами.\n\n"
        "Доступные команды:\n"
        "  /list — Мои задачи\n"
        "  /create — Создать задачу\n"
        "  /categories — Список категорий"
    )
