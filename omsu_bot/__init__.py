import logging
from sched import scheduler
from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.types import TelegramObject
from typing import Any, Awaitable, Callable, Dict

from pytz import timezone

from omsu_bot.config import Config
from omsu_bot.database import Database
from omsu_bot.handlers.admin import Admin
from omsu_bot.handlers.groups import Groups
from omsu_bot.handlers.menu import Menu
from omsu_bot.handlers.about import About
from omsu_bot.handlers.schedule import Schedule
from omsu_bot.handlers.settings import Settings
from omsu_bot.handlers.registration import Registration
from omsu_bot.services.broadcaster import broadcast

# debug import
# from omsu_bot.handlers.test import Test
# from omsu_bot.handlers.haduli import Haduli

class TaskScheduler(BaseMiddleware):
	def __init__(self, scheduler: AsyncIOScheduler) -> None:
		super().__init__()
		self._scheduler = scheduler

	async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]) -> Any:
		data["scheduler"] = self._scheduler
		return await handler(event, data)

class OMSUBot:
	tg: Bot
	
	def __init__(self, cfg: Config):
		self.config = cfg
		
		scheduler = AsyncIOScheduler(timezone=self.config.bot.timezone)
		self.scheduler = scheduler

		self.fsm_storage = get_fsm_storage(cfg)
		tg = Bot(token=cfg.bot.token, parse_mode="HTML")
		dp = Dispatcher(storage=self.fsm_storage)
		dp.update.middleware(
			TaskScheduler(scheduler=scheduler)
		)

		self.tg = tg
		self.dispatcher = dp
		self.db = Database(cfg.db.driver, cfg.db.user, cfg.db.password, cfg.db.host, cfg.db.port,
						   cfg.db.database)
		
		scheduler.add_job(Schedule.schedule_scheduler, "cron", hour=23, minute=49, args=(self.tg, self.db, self.config))

		handler_list = [Registration(), Menu(), Schedule(), Admin(), Settings(), About(), Groups()]

		self.handlers = handler_list

	async def launch(self):
		try:
			await self.db.launch()
			
			self.scheduler.start()

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
