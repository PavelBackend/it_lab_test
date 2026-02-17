from datetime import datetime, timezone, timedelta

ADAK_TZ = timezone(timedelta(hours=-10))
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import TextInput

from infrastructure.api_client.backend_client import BackendAPIClient

router = Router()


class CreateTaskSG(StatesGroup):
    """Состояния диалога создания задачи."""
    title = State()
    description = State()
    category = State()
    ask_due_date = State()
    due_date_input = State()


async def get_categories_data(dialog_manager: DialogManager, **kwargs):
    """Получить список категорий для диалога."""
    try:
        async with BackendAPIClient() as client:
            categories = await client.get_categories()
        return {
            "categories": [(cat.id, cat.name) for cat in categories],
            "has_categories": bool(categories),
        }
    except Exception:
        return {"categories": [], "has_categories": False}


async def on_title_entered(message: Message, widget, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["title"] = text
    await dialog_manager.next()


async def on_description_entered(message: Message, widget, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["description"] = text
    await dialog_manager.next()


async def on_category_selected(
    callback: CallbackQuery, widget, dialog_manager: DialogManager, item_id: str
):
    dialog_manager.dialog_data["category_id"] = item_id
    await dialog_manager.next()


async def on_skip_category(callback: CallbackQuery, button, dialog_manager: DialogManager):
    dialog_manager.dialog_data["category_id"] = None
    await dialog_manager.next()


async def on_set_due_date(callback: CallbackQuery, button, dialog_manager: DialogManager):
    """Пользователь хочет установить срок."""
    await dialog_manager.next()


async def on_skip_due_date(callback: CallbackQuery, button, dialog_manager: DialogManager):
    """Пользователь пропускает срок — сразу создаём задачу."""
    dialog_manager.dialog_data["due_date"] = None
    await _create_task(callback.message, dialog_manager)


async def on_due_date_entered(message: Message, widget, dialog_manager: DialogManager, text: str):
    """Обработать введённую дату."""
    formats = ["%d.%m.%Y %H:%M", "%d.%m.%Y", "%Y-%m-%d %H:%M", "%Y-%m-%d"]
    parsed = None
    for fmt in formats:
        try:
            parsed = datetime.strptime(text.strip(), fmt)
            break
        except ValueError:
            continue

    if not parsed:
        await message.answer(
            "Неверный формат даты.\n"
            "Введите дату в формате: ДД.ММ.ГГГГ ЧЧ:ММ\n"
            "Например: 25.02.2026 18:00"
        )
        return

    aware_dt = parsed.replace(tzinfo=ADAK_TZ)
    dialog_manager.dialog_data["due_date"] = aware_dt.isoformat()
    await _create_task(message, dialog_manager)


async def _create_task(message: Message, dialog_manager: DialogManager):
    """Создать задачу с собранными данными."""
    data = dialog_manager.dialog_data
    telegram_user_id = dialog_manager.middleware_data.get("event_from_user").id

    try:
        async with BackendAPIClient(telegram_user_id=telegram_user_id) as client:
            task = await client.create_task(
                title=data["title"],
                description=data["description"],
                category_id=data.get("category_id"),
                due_date=data.get("due_date"),
            )

        due_text = ""
        if task.due_date:
            try:
                due_dt = datetime.fromisoformat(task.due_date.replace("Z", "+00:00"))
                due_dt_msk = due_dt.astimezone(ADAK_TZ)
                due_text = f"\nСрок: {due_dt_msk.strftime('%d.%m.%Y %H:%M')} (Adak)"
            except Exception:
                pass

        await message.answer(
            f"Задача создана.\n\n"
            f"Название: {task.title}\n"
            f"Описание: {task.description}\n"
            f"Категория: {task.category_name or 'без категории'}"
            f"{due_text}"
        )
    except Exception as e:
        await message.answer(f"Ошибка при создании задачи: {str(e)}")
    finally:
        await dialog_manager.done()


create_task_dialog = Dialog(
    Window(
        Const("Создание задачи\n\nШаг 1 из 4: Введите название задачи:"),
        TextInput(id="title_input", on_success=on_title_entered),
        state=CreateTaskSG.title,
    ),
    Window(
        Const("Шаг 2 из 4: Введите описание задачи:"),
        TextInput(id="description_input", on_success=on_description_entered),
        state=CreateTaskSG.description,
    ),
    Window(
        Const("Шаг 3 из 4: Выберите категорию или пропустите:"),
        Select(
            Format("{item[1]}"),
            id="category_select",
            item_id_getter=lambda item: item[0],
            items="categories",
            on_click=on_category_selected,
        ),
        Button(Const("Без категории"), id="skip_category", on_click=on_skip_category),
        getter=get_categories_data,
        state=CreateTaskSG.category,
    ),
    Window(
        Const(
            "Шаг 4 из 4: Установить срок выполнения?\n\n"
            "Celery отправит вам уведомление в Telegram, когда срок будет подходить."
        ),
        Button(Const("Установить срок"), id="set_due_date", on_click=on_set_due_date),
        Button(Const("Без срока"), id="skip_due_date", on_click=on_skip_due_date),
        state=CreateTaskSG.ask_due_date,
    ),
    Window(
        Const(
            "Введите дату и время срока (часовой пояс America/Adak, UTC-10):\n\n"
            "Формат: ДД.ММ.ГГГГ ЧЧ:ММ\n"
            "Например: 25.02.2026 08:00"
        ),
        TextInput(id="due_date_input", on_success=on_due_date_entered),
        state=CreateTaskSG.due_date_input,
    ),
)


@router.message(Command("create"))
async def cmd_create_task(message: Message, dialog_manager: DialogManager):
    """Запустить диалог создания задачи."""
    await dialog_manager.start(CreateTaskSG.title, mode=StartMode.RESET_STACK)
