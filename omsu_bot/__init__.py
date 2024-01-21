import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from omsu_bot.config import Config
from omsu_bot.database import Database
from omsu_bot.handlers.admin import Administration
from omsu_bot.handlers.menu import Menu
from omsu_bot.handlers.schedule import Schedule
from omsu_bot.handlers.settings import Settings
from omsu_bot.handlers.registration import Registration
from omsu_bot.handlers.test import Test
from omsu_bot.services.broadcaster import broadcast


class OMSUBot:
	tg: Bot
	
	def __init__(self, cfg: Config):
		self.config = cfg

		self.fsm_storage = get_fsm_storage(cfg)
		tg = Bot(token=cfg.bot.token, parse_mode="HTML")
		dp = Dispatcher(storage=self.fsm_storage)

		self.tg = tg
		self.dispatcher = dp

		self.db = Database(cfg.db.driver, cfg.db.user, cfg.db.password, cfg.db.host, cfg.db.port,
						   cfg.db.database)

		handler_list = [Registration(), Menu(), Administration(), Settings(), Schedule()]

		self.handlers = handler_list

	async def launch(self):
		try:
			await self.db.launch()

			for h in self.handlers:
				await h.enable(self)

			tg = self.tg

			await broadcast(tg, self.config.bot.admin_ids, "Бот запущен")

			await tg.delete_webhook(drop_pending_updates=True)

			await self.dispatcher.start_polling(tg)
		finally:
			await self.shutdown()
	
	async def shutdown(self):
		logging.error("Bot shutting down...")
		await self.db.shutdown()
		logging.error("Bot shutdown success!")


def get_fsm_storage(cfg: Config) -> MemoryStorage:
	return MemoryStorage()
