from cgitb import text
from mailbox import Message
import aiogram
import sqlalchemy as sa
import sqlalchemy.orm as sorm

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup
import aiogram.types
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.keyboard import InlineKeyboardBuilder

import omsu_bot.data.language as lang
from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import RouterHandler
from omsu_bot.database.models import User, Student, Teacher


class MenuForm(StatesGroup):
	async def main_menu_message(bot, context: FSMContext, user: aiogram.types.User = None):
		data = await context.get_data()

		if not bot.db.is_online():
			return dict(
				text=lang.user_error_database_connection
			)

		inline_menu = (
			InlineKeyboardBuilder()
				.button(text="Расписание", callback_data="main_menu_schedule")
		)

		sess: sorm.Session = bot.db.session

		with sess.begin():
			db_user: User | None = sess.execute(sa.select(User).where(User.tg_id == user.id)).scalar_one_or_none()
			if db_user:

				if db_user.role_id == "student":
					student: Student = sess.execute(sa.select(Student).where(Student.user_id == db_user.id_)).scalar_one_or_none()
					if student:
						if student.is_moderator:
							inline_menu.button(text="Админ-меню", callback_data="main_menu_admin")
					else:
						return dict(text=lang.user_error_database_logic)
				
				elif db_user.role_id == "teacher":
					teacher: Teacher = sess.execute(sa.select(Teacher).where(Teacher.user_id == db_user.id)).scalar_one_or_none()
					if not teacher:
						return dict(text=lang.user_error_database_logic)
			else:
				return dict(
					text=lang.user_error_auth_unknown
				)
		
		
		return dict(
			text=lang.user_menu_description,
			reply_markup=
				inline_menu
					.button(text="Настройкиsdlakaafskfsdkfsad", callback_data="main_menu_settings")
					.button(text="О боте", callback_data="main_menu_about")
					.adjust(1, 2)
					.as_markup()
		)
	
	
	main_menu = HandlerState(message_handler=main_menu_message)


class Menu(RouterHandler):
	def __init__(self):
		super().__init__()
		
		router: Router = self.router

		@router.message(F.text == "Главное меню")
		async def handle_schedule(msg: Message, state: FSMContext):
			async with ChatActionSender.typing(chat_id=msg.chat.id, bot=self.bot.tg):
				MenuForm.main_menu.message_send(self.bot, state, msg.chat, msg.message_id)
