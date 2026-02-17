"""Main bot entry point."""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs
from decouple import config
from redis.asyncio import Redis

from application.handlers import start
from application.dialogs import task_list
from application.dialogs.task_create import router as create_router, create_task_dialog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Запустить бота."""
    bot_token = config('TELEGRAM_BOT_TOKEN')
    bot = Bot(token=bot_token)

    redis_url = config('REDIS_URL', default='redis://redis:6379/1')
    redis = Redis.from_url(redis_url)
    storage = RedisStorage(redis, key_builder=DefaultKeyBuilder(with_destiny=True))

    dp = Dispatcher(storage=storage)

    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(task_list.router)
    dp.include_router(create_router)
    dp.include_router(create_task_dialog)

    # Обязательная инициализация aiogram-dialog
    setup_dialogs(dp)

    logger.info("Бот запускается...")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        await redis.aclose()


if __name__ == '__main__':
    asyncio.run(main())
