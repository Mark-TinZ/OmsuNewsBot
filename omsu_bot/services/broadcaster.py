import asyncio
import logging
from typing import Union

from aiogram import Bot, exceptions
from aiogram.types import InlineKeyboardMarkup, InputFile


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
		logging.error("Telegram server says - Bad Request: chat not found")
	except exceptions.TelegramForbiddenError:
		logging.error(f"Target [ID:{user_id}]: got TelegramForbiddenError")
	except exceptions.TelegramRetryAfter as e:
		logging.error(
			f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds."
		)
		await asyncio.sleep(e.retry_after)
		return await send_message(
			bot, user_id, text, disable_notification, reply_markup, parse_mode
		)
	except exceptions.TelegramAPIError:
		logging.exception(f"Target [ID:{user_id}]: failed")
	else:
		logging.info(f"Target [ID:{user_id}]: success")
		return True
	return False

async def send_photo(
		bot: Bot,
		user_id: Union[int, str],
		caption: str,
		photo: Union[InputFile, str],
		disable_notification: bool = False,
		reply_markup: InlineKeyboardMarkup = None,
		parse_mode: str = "Markdown"
) -> bool:
	
	try:
		await bot.send_photo(
			user_id=user_id,
			photo=photo,
			caption=caption,
			disable_notification=disable_notification,
			reply_markup=reply_markup,
			parse_mode=parse_mode
		)
	except exceptions.TelegramBadRequest as e:
		logging.error("Telegram server says - Bad Request: chat not found")
	except exceptions.TelegramForbiddenError:
		logging.error(f"Target [ID:{user_id}]: got TelegramForbiddenError")
	except exceptions.TelegramRetryAfter as e:
		logging.error(
			f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds."
		)
		await asyncio.sleep(e.retry_after)
		return await bot.send_photo(
			user_id=user_id,
			photo=photo,
			caption=caption,
			disable_notification=disable_notification,
			reply_markup=reply_markup,
			parse_mode=parse_mode
		)
	except exceptions.TelegramAPIError:
		logging.exception(f"Target [ID:{user_id}]: failed")
	else:
		logging.info(f"Target [ID:{user_id}]: success")
		return True
	return False

async def forward_messages(
		bot: Bot,
		chat_id: Union[int, str],
		from_chat_id: Union[int, str],
		message_ids: list,
		message_thread_id: int = None,
		disable_notification: bool = None,
		protect_content: bool = None,
		request_timeout: int = None
	) -> bool:
	try:
		await bot.forward_messages(
			chat_id=chat_id,
			from_chat_id=from_chat_id,
			message_ids=message_ids,
			message_thread_id=message_thread_id,
			disable_notification=disable_notification,
			protect_content=protect_content,
			request_timeout=request_timeout
		)
	except exceptions.TelegramBadRequest as e:
		logging.error("Telegram server says - Bad Request: chat not found")
	except exceptions.TelegramForbiddenError:
		logging.error(f"Target [ID:{chat_id}]: got TelegramForbiddenError")
	except exceptions.TelegramRetryAfter as e:
		logging.error(
			f"Target [ID:{chat_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds."
		)
		await asyncio.sleep(e.retry_after)
		return await bot.forward_messages(
			chat_id=chat_id,
			from_chat_id=from_chat_id,
			message_ids=message_ids,
			message_thread_id=message_thread_id,
			disable_notification=disable_notification,
			protect_content=protect_content,
			request_timeout=request_timeout
		)
	except exceptions.TelegramAPIError:
		logging.exception(f"Target [ID:{chat_id}]: failed")
	else:
		logging.info(f"Target [ID:{chat_id}]: success")
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
		logging.info(f"{count} messages successful sent.")

	return count

class Broadcast():
	def __init__(
			self, 
			bot: Bot, 
			chat_id: Union[int, str], 
			protect_content: bool, 
			disable_notification: bool, 
			**kwargs
	):
		self.bot: Bot = bot
		self.chat_id: Union[int, str] = chat_id
		self.protect_content: bool = protect_content
		self.disable_notification: bool = disable_notification
		self.kwargs = kwargs

	def send_message(
			self, 
			text: str, 
			reply_markup: InlineKeyboardMarkup = None,
			parse_mode: str = "Markdown"
	):
		pass