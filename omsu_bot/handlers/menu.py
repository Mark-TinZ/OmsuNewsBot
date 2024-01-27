import logging
import sqlalchemy as sa
import sqlalchemy.orm as sorm

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton
from aiogram.utils.chat_action import ChatActionSender

from omsu_bot import utils
from omsu_bot.config import Config
import omsu_bot.data.language as lang
from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import RouterHandler
from omsu_bot.handlers.about import AboutForm
from omsu_bot.handlers.admin import AdminForm
from omsu_bot.handlers.schedule import ScheduleForm
from omsu_bot.handlers.settings import SettingsForm
from omsu_bot.database.models import Group, User, Student, Teacher




class MenuForm(StatesGroup):
	async def menu_main_message(self, bot, context: FSMContext):
		# data = await context.get_data()

		# if not bot.db.is_online():
		# 	return dict(
		# 		text=lang.user_error_database_connection
		# 	)

		# sess: sorm.Session = bot.db.session

		# with sess.begin():
		# 	user: User | None = sess.execute(sa.select(User).where(User.tg_id == tg_id)).scalar_one_or_none()

		# 	if not user:
		# 		return dict(text=lang.user_error_auth_unknown)

		# 	if user.role_id == "student":
		# 		union = sess.execute(
		# 			sa.select(Student, Group)
		# 			.where(Student.user_id == user.id_)
		# 			.join(Group, Student.group_id == Group.id_)
		# 		).first()

		# 		if not union or len(union) != 2:
		# 			return dict(text=lang.user_error_database_logic)
		# 		student, group = union
		# 		if student.is_moderator:
		# 			reply_menu.row(KeyboardButton(text="Управление группой"))
		# 	elif user.role_id == "teacher":
		# 		teacher: Teacher = sess.execute(sa.select(Teacher).where(Teacher.user_id == user.id_)).scalar_one_or_none()
		# 		if not teacher:
		# 			return dict(text=lang.user_error_database_logic)
		

		tg_id = context.key.user_id
		cfg = bot.config

		reply_menu = (
			ReplyKeyboardBuilder()
				.button(text="Расписание", callback_data="main_menu_schedule")
				.button(text="Настройки", callback_data="main_menu_settings")
				.button(text="О боте", callback_data="main_menu_about")
				.adjust(1, 2)
		)
		
		if tg_id in cfg.bot.admin_ids:
			reply_menu.row(KeyboardButton(text="Админ-меню"))
		
		
		
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
			if await utils.throttling_assert(state): return

			await ScheduleForm.schedule.message_send(self.bot, state, msg.chat, reply_to_message_id=msg.message_id)

		@router.message(F.text.lower() == "настройки")
		async def handle_setting(msg: types.Message, state: FSMContext):
			if await utils.throttling_assert(state): return

			await SettingsForm.settings.message_send(self.bot, state, msg.chat, reply_to_message_id=msg.message_id)

		@router.message(F.text.lower().in_(("/help", "о боте")))
		async def handle_about(msg: types.Message, state: FSMContext):
			if await utils.throttling_assert(state): return

			await AboutForm.about.message_send(self.bot, state, msg.chat, reply_to_message_id=msg.message_id)

		@router.message(F.text.lower() == "админ-меню")
		async def handle_admin(msg: types.Message, state: FSMContext):
			if await utils.throttling_assert(state): return

			if msg.from_user.id not in self.bot.config.bot.admin_ids:
				return

			await AdminForm.admin.message_send(self.bot, state, msg.chat, reply_to_message_id=msg.message_id)

		# @router.message(F.text.lower() == "управление группой")
		# async def handle_moderator(msg: types.Message, state: FSMContext):
		# 	if await utils.throttling_assert(state): return

		# 	if not self.bot.db.is_online(): await msg.answer(text=lang.user_error_database_connection)

		# 	tg_id = msg.from_user.id
		# 	sess: sorm.Session = self.bot.db.session
			
		# 	with sess.begin():
		# 		user: User | None = sess.execute(sa.select(User).where(User.tg_id == tg_id)).scalar_one_or_none()

		# 		if not user: return dict(text=lang.user_error_auth_unknown)
				
		# 		if user.role_id != "student": return

		# 		union = sess.execute(
		# 			sa.select(Student, Group)
		# 			.where(Student.user_id == user.id_)
		# 			.join(Group, Student.group_id == Group.id_)
		# 		).first()

		# 		if not union or len(union) != 2:
		# 			return dict(text=lang.user_error_database_logic)
		# 		student, group = union
		# 		if not student.is_moderator: return
				
		# 		await state.update_data(groups_group_id=group.id_)
			
		# 	await AdminForm.group_settings.message_send(self.bot, state, msg.chat, reply_to_message_id=msg.message_id)
