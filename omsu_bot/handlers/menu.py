from re import T
import sqlalchemy as sa
import sqlalchemy.orm as sorm

from aiogram import Router, types, F
from aiogram.fsm.state import StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.chat_action import ChatActionSender

import omsu_bot.data.language as lang
from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import RouterHandler
from omsu_bot.handlers.schedule import ScheduleForm
from omsu_bot.handlers.settings import SettingsForm
from omsu_bot.database.models import User, Student, Teacher




class MenuForm(StatesGroup):
	async def menu_main_message(self, bot, context: FSMContext, actor: types.User = None):
		data = await context.get_data()

		if not bot.db.is_online():
			return dict(
				text=lang.user_error_database_connection
			)

		reply_menu = (
			ReplyKeyboardBuilder()
				.button(text="Расписание", callback_data="main_menu_schedule")
				.button(text="Настройки", callback_data="main_menu_settings")
				.button(text="О боте", callback_data="main_menu_about")
				.adjust(1, 2)
		)

		sess: sorm.Session = bot.db.session

		with sess.begin():
			user: User | None = sess.execute(sa.select(User).where(User.tg_id == actor.id)).scalar_one_or_none()

			if user:
				if user.role_id == "student":
					student: Student = sess.execute(sa.select(Student).where(Student.user_id == user.id_)).scalar_one_or_none()
					if not student:
						return dict(text=lang.user_error_database_logic)

					if student.is_moderator:
							reply_menu.row(text="Админ-меню", callback_data="main_menu_admin")
				elif user.role_id == "teacher":
					teacher: Teacher = sess.execute(sa.select(Teacher).where(Teacher.user_id == user.id_)).scalar_one_or_none()
					if not teacher:
						return dict(text=lang.user_error_database_logic)
			else:
				return dict(
					text=lang.user_error_auth_unknown
				)
		
		
		return dict(
			text=lang.user_menu_description,
			reply_markup=reply_menu.as_markup(resize_keyboard=True)
		)
	
	menu_main = HandlerState(message_handler=menu_main_message)





class Menu(RouterHandler):
	def __init__(self):
		super().__init__()
		
		router: Router = self.router

		@router.message(F.text.lower() == "расписание")
		async def handle_schedule(msg: types.Message, state: FSMContext):
			async with ChatActionSender.typing(chat_id=msg.chat.id, bot=self.bot.tg):
				await ScheduleForm.schedule.message_send(self.bot, state, msg.chat, actor=msg.from_user)

		@router.message(F.text.lower() == "настройки")
		async def handle_setting(msg: types.Message, state: FSMContext):
			async with ChatActionSender.typing(chat_id=msg.chat.id, bot=self.bot.tg):
				await SettingsForm.settings.message_send(self.bot, state, msg.chat, actor=msg.from_user)

		@router.message(F.text.lower() == "о боте")
		async def handle_about(msg: types.Message, state: FSMContext):
			async with ChatActionSender.upload_video_note(chat_id=msg.chat.id, bot=self.bot.tg):
				video_note = types.FSInputFile("media/video/dragon-dance.mp4")
				await msg.answer_video_note(video_note)