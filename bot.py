import asyncio
import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder

from tgbot.database import Database
from tgbot.config import load_config
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


# def register_global_middlewares(dp: Dispatcher, config: Config):
# 	middleware_types = [
# 		ConfigMiddleware(config)
# 	]

# 	for middleware_type in middleware_types:
# 		dp.message.outer_middleware(middleware_type)
# 		dp.callback_query.outer_middleware(middleware_type)



def get_storage(config: any) -> MemoryStorage:
	return MemoryStorage()


async def main() -> None:
	setup_logging()

	config = load_config(".env")
	storage = get_storage(config)

	bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
	await bot.delete_webhook(drop_pending_updates=True)
	dp = Dispatcher(storage=storage)
	bot.config = config

	dp.include_routers(*routers_list)

	# register_global_middlewares(dp, config)
	db = Database(config.db.driver, config.db.user, config.db.password, config.db.host, config.db.port, config.db.database)
	await on_startup(bot, config.tg_bot.admin_ids)
	await dp.start_polling(bot)


if __name__ == '__main__':
	try:
		asyncio.run(main())
	except (KeyboardInterrupt, SystemExit):
		logging.error("Bot stopped!")
