import asyncio
import logging
from sys import stdout

from aiogram.fsm.storage.memory import MemoryStorage

from tgbot.config import load_config
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from tgbot.database.create_table import create_table_all
from tgbot.handlers import routers_list
from tgbot.services import broadcaster


async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, "Бот был запущен")


def setup_logging():
    log_level = logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
        stream=stdout
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


async def main():
    setup_logging()

    config = load_config(".env")
    storage = MemoryStorage()

    bot = Bot(token=config.tg_bot.token, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=storage)

    dp.include_routers(*routers_list)

    await on_startup(bot, config.tg_bot.admin_ids)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
        asyncio.run(create_table_all())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Бот был выключен!")
