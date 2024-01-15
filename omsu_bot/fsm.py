
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, Chat, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply

from omsu_bot import utils


class HandlerState(State):

	def __init__(self, name: str = None, text: str = None, reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply = None, parse_mode: str | None = "Markdown", register_context: bool = True, register_context_safe: bool = False, message_handler = None, message_edit_handler = None, message_send_handler = None, previous_state = None):
		super().__init__()

		# handlers
		self.message_handler = message_handler
		self.message_edit_handler = message_edit_handler
		self.message_send_handler = message_send_handler

		# preset
		self.text = text
		self.reply_markup = reply_markup
		self.parse_mode = parse_mode
		self.register_context = register_context
		self.register_context_safe = register_context_safe

		# state name (not implemented)
		self.name = name
		self.previous_state = previous_state

	# await request_number.message_edit(self.bot, state, msg)
	# await request_number.message_edit(self.bot, state, message_id, chat)
	async def message_edit(self, bot, context: FSMContext, message: Message | int, chat: Chat | int = None, *args, **kwargs):

		is_raw = isinstance(message, int)
		chat_id = None
		if is_raw:
			chat_id = chat if isinstance(chat, int) else chat.id

		if self.message_edit_handler:
			await self.message_edit_handler(self, bot, context, message, chat, *args, **kwargs)

		elif self.message_handler:
			data = await self.message_handler(self, bot, context, *args, **kwargs)

			if data:
				if is_raw:
					await bot.tg.edit_message_text(chat_id=chat_id, message_id=message, parse_mode=self.parse_mode, **data)
				else:
					await message.edit_text(parse_mode=self.parse_mode, **data)

		else:
			await context.set_state(self)
			if self.text:
				if is_raw:
					await bot.tg.edit_message_text(chat_id=chat_id, message_id=message, text=self.text, reply_markup=self.reply_markup, parse_mode=self.parse_mode)
				else:
					await message.edit_text(text=self.text, reply_markup=self.reply_markup, parse_mode=self.parse_mode)

	async def message_send(self, bot, context: FSMContext, chat: Chat | int, reply_to_message_id: int = None, *args, **kwargs):

		chat_id = chat if isinstance(chat, int) else chat.id

		if self.message_send_handler:
			return await self.message_send_handler(self, bot, chat, context, reply_to_message_id, *args, **kwargs)

		elif self.message_handler:
			data = await self.message_handler(self, bot, context, *args, **kwargs)

			if data:
				msg = await bot.tg.send_message(chat_id=chat_id, reply_to_message_id=reply_to_message_id, parse_mode=self.parse_mode, **data)
				if data.get("register_context", True):
					await utils.register_context(context, msg, safe=data.get("register_context_safe", False))
				return msg

		else:
			await context.set_state(self)
			if self.text:
				msg = await bot.tg.send_message(chat_id=chat_id, reply_to_message_id=reply_to_message_id, text=self.text, reply_markup=self.reply_markup, parse_mode=self.parse_mode)
				if self.register_context:
					await utils.register_context(context, msg, safe=self.register_context_safe)
				return msg




