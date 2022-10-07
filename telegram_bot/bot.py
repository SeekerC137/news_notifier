import logging
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.executor import start_webhook

from telegram_bot.handlers.start import register_handlers

from config import BOT_TOKEN

WEBHOOK_HOST = 'https://news-notifier.fly.dev'
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = 'localhost'
WEBAPP_PORT = 8080


bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)


async def run_bot() -> None:

    # Настройка логирования в stdout
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    dp = Dispatcher(bot, storage=MemoryStorage())

    register_handlers(dp)

    await set_commands(bot)

    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )


async def set_commands(_bot: Bot) -> None:
    commands = [
        BotCommand(command="/start", description="Главное меню"),
    ]
    await _bot.set_my_commands(commands)


async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)
    # insert code here to run it after start


async def on_shutdown(_dp):
    logging.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await _dp.storage.close()
    await _dp.storage.wait_closed()

    logging.warning('Bye!')
