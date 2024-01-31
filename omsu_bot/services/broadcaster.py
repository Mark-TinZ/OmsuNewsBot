import asyncio
import logging
from typing import Any, Union

from aiogram import Bot, exceptions
from aiogram.types import InlineKeyboardMarkup

logger = logging.getLogger(__name__)

async def send_message(
		bot: Bot,
		user_id: Union[int, str],
		text: str,
		disable_notification: bool = False,
		reply_markup: InlineKeyboardMarkup = None,
		parse_mode: str = "Markdown"
) -> bool:
	
	try:
		await bot.send_message(
			chat_id=user_id,
			text=text,
			disable_notification=disable_notification,
			reply_markup=reply_markup,
			parse_mode=parse_mode
		)
	except exceptions.TelegramBadRequest as e:
		logger.error("Telegram server says - Bad Request: chat not found")
	except exceptions.TelegramForbiddenError:
		logger.error(f"Target [ID:{user_id}]: got TelegramForbiddenError")
	except exceptions.TelegramRetryAfter as e:
		logger.error(
			f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds."
		)
		await asyncio.sleep(e.retry_after)
		return await send_message(
			bot, user_id, text, disable_notification, reply_markup, parse_mode
		)
	except exceptions.TelegramAPIError:
		logger.exception(f"Target [ID:{user_id}]: failed")
	else:
		logger.info(f"Target [ID:{user_id}]: success")
		return True
	return False

async def broadcast(
		bot: Bot,
		users: list[Union[str, int]],
		text: str,
		disable_notification: bool = False,
		reply_markup: InlineKeyboardMarkup = None,
		parse_mode: str = "Markdown"
) -> int:
	count = 0
	try:
		for user_id in users:
			if await send_message(
					bot, user_id, text, disable_notification, reply_markup, parse_mode
			):
				count += 1
			await asyncio.sleep(
				0.05
			)
	finally:
		logger.info(f"{count} messages successfully sent.")

	return count



class Broadcast():
	def __init__(
			self, 
			bot: Bot, 
			chat_ids: list[Union[int, str]], 
			protect_content: bool = False, 
			disable_notification: bool = False, 
			flood_sleep: bool = False
	):
		self.bot: Bot = bot
		self.chat_ids: list[Union[int, str]] = chat_ids
		self.protect_content: bool = protect_content
		self.disable_notification: bool = disable_notification
		self.flood_sleep: bool = flood_sleep


	async def send_message(self, *args, **kwargs) -> bool:
		import tracemalloc
		tracemalloc.start()
		for chat_id in self.chat_ids:
			try:
				self.bot.send_message(
					*args,
					chat_id=chat_id,
					disable_notification=self.disable_notification,
					**kwargs
				)
			except exceptions.TelegramRetryAfter as e:
				await asyncio.sleep(e.retry_after)
				self.bot.send_message(
					*args,
					chat_id=chat_id,
					disable_notification=self.disable_notification,
					**kwargs
				)
			

	async def send_photo(self, *args, **kwargs) -> bool:
		for chat_id in self.chat_ids:
			try:
				await self.bot.send_photo(
					*args,
					user_id=chat_id,
					disable_notification=self.disable_notification,
					**kwargs
				)
			except exceptions.TelegramRetryAfter as e:
				await self.bot.send_photo(
					*args,
					user_id=chat_id,
					disable_notification=self.disable_notification,
					**kwargs
				)