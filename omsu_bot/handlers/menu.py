from datetime import datetime
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
import omsu_bot.data.lang as lang
from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import RouterHandler
from omsu_bot.handlers.about import AboutForm
from omsu_bot.handlers.admin import AdminForm
from omsu_bot.handlers.schedule import ScheduleForm
from omsu_bot.handlers.settings import SettingsForm
from omsu_bot.database.models import Group, User, Student, Teacher
from omsu_bot.filters import MainFilter

logger = logging.getLogger(__name__)


class MenuForm(StatesGroup):
	async def menu_main_message(self, bot, context: FSMContext):
		tg_id = context.key.user_id
		cfg = bot.config

		reply_menu = (
			ReplyKeyboardBuilder()
				.button(text="Расписание", callback_data="main_menu_schedule")
				.button(text="Настройки", callback_data="main_menu_settings")
				.button(text="О боте", callback_data="main_menu_about")
				.adjust(1, 2)
		)

		if tg_id in cfg.main.admin_ids:
			reply_menu.row(KeyboardButton(text="Админ-меню"))

		return dict(
			text=lang.user_menu_description,
			reply_markup=reply_menu.as_markup(resize_keyboard=True)
		)

	menu_main = HandlerState(message_handler=menu_main_message)

	async def menu_main_group_message(self, bot, context: FSMContext):
		reply_menu = (
			ReplyKeyboardBuilder()
				.button(text="Расписание", callback_data="main_menu_schedule")
		)

		return dict(
			text=lang.user_menu_description,
			reply_markup=reply_menu.as_markup(resize_keyboard=True)
		)
	
	menu_main_group = HandlerState(message_handler=menu_main_group_message)

	async def main_academic_message(select, bot, context: FSMContext):
		cfg = bot.config

		days_difference = (datetime.today().date() - cfg.main.academic_start).days 

		return dict(
			text=lang.academic_weeks.format(academic_week=(days_difference // 7) + 1)
		)
	
	main_academic = HandlerState(message_handler=main_academic_message)

class Menu(RouterHandler):
	def __init__(self) -> None:
		super().__init__()

		router: Router = self.router

		@router.message(MainFilter(allow_groups=True), F.text.lower() == "расписание")
		async def handle_schedule(msg: types.Message, state: FSMContext) -> None:
			if await utils.throttling_assert(state): return

			await ScheduleForm.schedule.message_send(self.bot, state, msg.chat, reply_to_message_id=msg.message_id)
<<<<<<< HEAD
=======
			
>>>>>>> b3cbe8f121d82c6ca395df027451653658db9799

		@router.message(MainFilter(), F.text.lower() == "настройки")
		async def handle_setting(msg: types.Message, state: FSMContext) -> None:
			if await utils.throttling_assert(state): return

			await SettingsForm.settings.message_send(self.bot, state, msg.chat, reply_to_message_id=msg.message_id)

		@router.message(MainFilter(), F.text.lower().in_(("/help", "о боте")))
		async def handle_about(msg: types.Message, state: FSMContext) -> None:
			if await utils.throttling_assert(state): return

			await AboutForm.about.message_send(self.bot, state, msg.chat, reply_to_message_id=msg.message_id)

		@router.message(MainFilter(), F.text.lower() == "/academic")
		async def handle_academic(msg: types.Message, state: FSMContext) -> None:
			if await utils.throttling_assert(state): return

			await MenuForm.main_academic.message_send(self.bot, state, msg.chat, reply_to_message_id=msg.message_id)

		@router.message(MainFilter(), F.text.lower() == "админ-меню")
		async def handle_admin(msg: types.Message, state: FSMContext) -> None:
			if await utils.throttling_assert(state): return

			if msg.from_user.id not in self.bot.config.main.admin_ids:
				return

			await AdminForm.admin.message_send(self.bot, state, msg.chat, reply_to_message_id=msg.message_id)
