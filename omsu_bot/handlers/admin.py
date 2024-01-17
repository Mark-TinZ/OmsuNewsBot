import sqlalchemy as sa
import sqlalchemy.orm as sorm

from aiogram import Router
from aiogram.fsm.state import StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from omsu_bot import utils
import omsu_bot.data.language as lang
from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import RouterHandler



class AdministrationForm(StatesGroup):
	@staticmethod
	async def admin_message(self, bot, context: FSMContext):
		return dict(
			text=lang.user_admin_description,
			reply_markup=
				InlineKeyboardBuilder()
				.button(text="Расписание", callback_data="admin_menu_schedule")
				.as_markup(),
			register_context=True
		)
	
	admin = HandlerState(message_handler=admin_message)



class Administration(RouterHandler):
	def __init__(self):
		super().__init__()
		
		router: Router = self.router

