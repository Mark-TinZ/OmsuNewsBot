
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, Chat, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply


class HandlerState(State):

	def __init__(self, name: str = None, text: str = None, reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply = None, parse_mode: str | None = "MarkdownV2", message_handler = None, message_edit_handler = None, message_send_handler = None):
		super().__init__()
		self.message_handler = message_handler
		self.message_edit_handler = message_edit_handler
		self.message_send_handler = message_send_handler
		self.text = text
		self.reply_markup = reply_markup
		self.parse_mode = parse_mode
		self.name = name

	async def message_edit(self, bot, context: FSMContext, message: Message | int, chat: Chat | int = None, *args, **kwargs):
		await context.set_state(self)

		is_raw = isinstance(message, int)
		chat_id = None
		if is_raw:
			chat_id = chat if isinstance(chat, int) else chat.id

		if self.message_edit_handler:
			await self.message_edit_handler(bot, context, message, chat, *args, **kwargs)

		elif self.message_handler:
			data = await self.message_handler(bot, context, *args, **kwargs)

			if data:
				if is_raw:
					await bot.tg.edit_message_text(chat_id=chat_id, message_id=message, **data)
				else:
					await message.edit_text(**data)

		else:
			if not self.text is None:
				if is_raw:
					await bot.tg.edit_message_text(chat_id=chat_id, message_id=message, text=self.text, reply_markup=self.reply_markup, parse_mode=self.parse_mode)
				else:
					await message.edit_text(text=self.text, reply_markup=self.reply_markup, parse_mode=self.parse_mode)

	async def message_send(self, bot, context: FSMContext, chat: Chat | int, reply_to_message_id: int = None, *args, **kwargs):
		await context.set_state(self)

		chat_id = chat if isinstance(chat, int) else chat.id

		if self.message_send_handler:
			await self.message_send_handler(bot, chat, context, reply_to_message_id, *args, **kwargs)

		elif self.message_handler:
			data = await self.message_handler(bot, context, *args, **kwargs)

			if data:
				await bot.tg.send_message(chat_id=chat_id, reply_to_message_id=reply_to_message_id, **data)

		else:
			if not self.text is None:
				await bot.tg.send_message(chat_id=chat_id, reply_to_message_id=reply_to_message_id, text=self.text, reply_markup=self.reply_markup, parse_mode=self.parse_mode)





