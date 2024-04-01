import logging

from aiogram.types import TelegramObject
from typing import Any, Awaitable, Callable, Dict
from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from omsu_bot.config import Config
from omsu_bot.database import Database
from omsu_bot.handlers.menu import Menu
from omsu_bot.handlers.about import About
from omsu_bot.handlers.admin import Admin
from omsu_bot.handlers.groups import Groups
from omsu_bot.handlers.schedule import Schedule
from omsu_bot.handlers.settings import Settings
from omsu_bot.handlers.scope_work import ScopeWork
from omsu_bot.services.broadcaster import Broadcast
from omsu_bot.handlers.registration import Registration

class TaskScheduler(BaseMiddleware):
	def __init__(self, scheduler: AsyncIOScheduler) -> None:
		super().__init__()
		self._scheduler = scheduler

	async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]) -> Any:
		data["scheduler"] = self._scheduler
		return await handler(event, data)

class OMSUBot:
	tg: Bot

	def __init__(self, config: Config) -> None:
		self.config = config
		main_cfg = config.main

		scheduler = AsyncIOScheduler(timezone=main_cfg.timezone)
		self.scheduler = scheduler

		self.fsm_storage = get_fsm_storage()
		tg = Bot(token=self.config.bot.token, parse_mode=main_cfg.parse_mode)
		dp = Dispatcher(storage=self.fsm_storage)
		dp.update.middleware(
			TaskScheduler(scheduler=scheduler)
		)

		self.tg = tg
		self.dispatcher = dp
		db_cfg = config.db

		self.db = Database(db_cfg)
		scheduler.add_job(Schedule.schedule_scheduler, "cron", hour=18, minute=0, args=(self.tg, self.db, self.config))
		# scheduler.add_job(Schedule.schedule_scheduler, "interval", seconds=10, args=(self.tg, self.db, self.config))

		handler_list = [Registration(), Menu(), Schedule(), Admin(), Settings(), About(), Groups(), ScopeWork()]

		self.handlers = handler_list

	async def start(self) -> None:
		try:
			await self.db.launch()
			
			self.scheduler.start()

			for h in self.handlers:
				await h.enable(self)

			tg = self.tg
			mailing = Broadcast(tg, self.config.main.admin_ids)
			await mailing.send_message(text="Бот запущен")

			await tg.delete_webhook(drop_pending_updates=True)

			await self.dispatcher.start_polling(tg)
		finally:
			await self.shutdown()
	
	async def shutdown(self) -> None:
		logging.error("Bot shutting down...")
		await self.db.shutdown()
		logging.error("Bot shutdown success!")
		logging.shutdown()


def get_fsm_storage() -> MemoryStorage:
	return MemoryStorage()
