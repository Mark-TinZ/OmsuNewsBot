import asyncio
import logging
from typing import Union

from aiogram import Bot, exceptions

logger = logging.getLogger(__name__)


class Broadcast():
	def __init__(
			self, 
			bot: Bot, 
			chat_ids: list[Union[int, str]], 
			protect_content: bool = False, 
			disable_notification: bool = False, 
			flood_sleep: bool = False
	) -> None:
		self.bot: Bot = bot
		self.chat_ids: list[Union[int, str]] = chat_ids
		self.protect_content: bool = protect_content
		self.disable_notification: bool = disable_notification
		self.flood_sleep: bool = flood_sleep

	async def send_message(self, *args, **kwargs) -> None:
		for chat_id in self.chat_ids:
			try:
				await self.bot.send_message(
					*args,
					chat_id=chat_id,
					disable_notification=self.disable_notification,
					**kwargs
				)
			except exceptions.TelegramRetryAfter as e:
				logger.info(f"Telegram: retry after {e.retry_after} sec")
				await asyncio.sleep(e.retry_after)
				await self.bot.send_message(
					*args,
					chat_id=chat_id,
					disable_notification=self.disable_notification,
					**kwargs
				)
			except Exception as e:
				logger.warn(f"Error sending message to chat ({chat_id}) {type(e)}") 

	async def send_photo(self, *args, **kwargs) -> None:
		for chat_id in self.chat_ids:
			try:
				await self.bot.send_photo(
					*args,
					chat_id=chat_id,
					disable_notification=self.disable_notification,
					**kwargs
				)
			except exceptions.TelegramRetryAfter as e:
				logger.warning(f"Telegram: retry after {e.retry_after} sec")
				await asyncio.sleep(e.retry_after)
				await self.bot.send_photo(
					*args,
					chat_id=chat_id,
					disable_notification=self.disable_notification,
					**kwargs
				)