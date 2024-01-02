import asyncio
import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder

from tgbot.config import load_config
from tgbot.database.create_database import create_database
from tgbot.database.postgresql import db
from tgbot.handlers import routers_list
from tgbot.services import broadcaster


async def on_startup(bot: Bot, admin_ids: list[int]) -> None:
    await broadcaster.broadcast(bot, admin_ids, "Бот был запущен")


def setup_logging() -> None:
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


def get_storage(config: any) -> RedisStorage | MemoryStorage:
    if config.tg_bot.use_redis:
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()


async def main() -> None:
    setup_logging()

    config = load_config(".env")
    storage = get_storage(config)

    await db.connect(config.db.user, config.db.password, config.db.host, config.db.port, config.db.database)
    await create_database(db)

    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher(storage=storage)

    bot.config = config

    dp.include_routers(*routers_list)

    await on_startup(bot, config.tg_bot.admin_ids)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
