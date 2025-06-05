import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs
from redis.asyncio.client import Redis

from app_settings import AppSettings, load_settings
from bot.dialogs.ooh.dialogs import ooh_task_dialog
from bot.dialogs.ooh_settings.dialogs import ooh_settings_dialog
from bot.dialogs.radio.dialogs import radio_dialog
from bot.dialogs.radio_settings.dialogs import radio_settings_dialog
from bot.dialogs.tv.ru.nat.nat_dialogs import nat_affinity_task_dialog, nat_base_task_dialog
from bot.dialogs.tv.ru.reg.reg_dialogs import reg_affinity_task_dialog, reg_base_task_dialog
from bot.menu import router as menu_router
from bot.menu import set_commands

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

# Уровень WARNING для избежания засорения логов в терминале
logging.getLogger('aiogram').setLevel(logging.WARNING)
logging.getLogger('redis').setLevel(logging.WARNING)

log = logging.getLogger(__name__)


async def main():
    app_settings: AppSettings = load_settings()

    # Определение сервера Telegram API
    if app_settings.LOCALHOST:
        session = AiohttpSession(api=TelegramAPIServer.from_base(app_settings.LOCAL_SERVER_URL, is_local=True))
        bot: Bot = Bot(
            token=app_settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML), session=session
        )
    else:
        bot: Bot = Bot(
            token=app_settings.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

    redis_storage = RedisStorage(
        redis=Redis(host=app_settings.REDIS_HOST),
        key_builder=DefaultKeyBuilder(with_destiny=True),
    )

    dp = Dispatcher(storage=redis_storage)

    dp.startup.register(set_commands)
    dp.include_router(menu_router)
    dp.include_router(nat_base_task_dialog)
    dp.include_router(nat_affinity_task_dialog)
    dp.include_router(reg_base_task_dialog)
    dp.include_router(reg_affinity_task_dialog)
    dp.include_router(ooh_task_dialog)
    dp.include_router(ooh_settings_dialog)
    dp.include_router(radio_dialog)
    dp.include_router(radio_settings_dialog)

    setup_dialogs(dp)

    # Старт поллинга Telegram API
    log.info('Ожидание апдейтов от Telegram API...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
