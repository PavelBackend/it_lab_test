

class TelegramUserMiddleware:
    """
    Читает заголовок X-Telegram-User-Id и сохраняет telegram_id
    в профиле текущего пользователя.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        telegram_id = request.headers.get("X-Telegram-User-Id")
        if telegram_id and request.user.is_authenticated:
            try:
                from apps.todo.infrastructure.persistence.models import UserProfile
                UserProfile.objects.update_or_create(
                    user=request.user,
                    defaults={"telegram_id": int(telegram_id)},
                )
            except (ValueError, Exception):
                pass

        return response
