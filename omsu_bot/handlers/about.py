import logging

from aiogram import Router
from aiogram.fsm.state import StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

import omsu_bot.data.language as lang
from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import RouterHandler

logger = logging.getLogger(__name__)

class AboutForm(StatesGroup):
	@staticmethod
	async def about_message(self, bot, context: FSMContext):
		return dict(
			text=lang.user_about,
			reply_markup=
				InlineKeyboardBuilder()
					.button(text="Предложить идею", url="https://t.me/MarkT1n")
					.button(text="Сообщить о проблеме", url="https://t.me/MarkT1n")
					.as_markup()
		)
	
	about = HandlerState(message_handler=about_message)

class About(RouterHandler):
	def __init__(self):
		super().__init__()
		
		router: Router = self.router