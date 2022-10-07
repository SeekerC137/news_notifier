import logging

from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from telegram_bot.handlers.start import register_handlers

from config import BOT_TOKEN


bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())


async def run_bot() -> None:

    # Настройка логирования в stdout
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    register_handlers(dp)

    await set_commands(bot)

    await dp.start_polling()


async def set_commands(_bot: Bot) -> None:
    commands = [
        BotCommand(command="/start", description="Главное меню"),
    ]
    await _bot.set_my_commands(commands)
