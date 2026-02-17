import httpx
from celery import shared_task
from django.conf import settings
from datetime import timedelta, timezone as dt_timezone

ADAK_TZ = dt_timezone(timedelta(hours=-10))

from apps.todo.infrastructure.persistence.models import Task


def _send_telegram_message(telegram_id: int, text: str) -> None:
    """Синхронная отправка сообщения в Telegram."""
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
    if not token or not telegram_id:
        return
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        httpx.post(url, json={"chat_id": telegram_id, "text": text}, timeout=10)
    except Exception as e:
        print(f"Ошибка отправки Telegram уведомления: {e}")


@shared_task(name="notify_task_due")
def notify_task_due(task_id: str):
    """
    Отправляет уведомление о наступившем сроке для конкретной задачи.
    Запускается через apply_async(eta=due_date) в момент создания/обновления задачи.
    """
    try:
        task = Task.objects.select_related(
            "user", "user__profile", "category"
        ).get(id=task_id, is_completed=False)
    except Task.DoesNotExist:
        return f"Задача {task_id} не найдена или уже выполнена"

    due_msk = task.due_date.astimezone(ADAK_TZ)
    due_str = due_msk.strftime("%d.%m.%Y %H:%M")

    category_info = f" [{task.category.name}]" if task.category else ""
    text = (
        f"Время выполнения задачи наступило!\n\n"
        f"Задача: {task.title}{category_info}\n"
        f"Срок: {due_str} (МСК)\n\n"
        f"Не забудьте выполнить задачу!"
    )

    try:
        telegram_id = task.user.profile.telegram_id
    except Exception:
        telegram_id = None

    if telegram_id:
        _send_telegram_message(telegram_id, text)
        return f"Уведомление отправлено для задачи {task_id}"

    return f"Нет telegram_id для задачи {task_id}"
