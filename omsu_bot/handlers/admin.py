import logging
import sqlalchemy as sa
import sqlalchemy.orm as sorm

from aiogram import Router
from aiogram.fsm.state import StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.chat_action import ChatActionSender

from omsu_bot import utils
import omsu_bot.data.language as lang
from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import RouterHandler
from omsu_bot.database.models import User, Student, Teacher

logger = logging.getLogger(__name__)


class AdministrationForm(StatesGroup):
	@staticmethod
	async def admin_message(self, bot, context: FSMContext):
		sess: sorm.Session = bot.db.session
		tg_id = context.key.user_id
		cfg = bot.config

		with sess.begin():
			user: User | None = sess.execute(sa.select(User).where(User.tg_id == tg_id)).scalar_one_or_none()

			if not user:
				logger.error(f"id={context.key.user_id}, Вы не зарегистрированы!")
				return dict(text=lang.user_error_auth_unknown)
			
			if user.role_id == "student":
				student: Student = sess.execute(sa.select(Student).where(Student.user_id == user.id_)).scalar_one_or_none()
				if not student:
					logger.error(f"id={context.key.user_id}, Логическое исключение, запись в бд повреждена")
					return dict(text=lang.user_error_database_logic)
				if student.is_moderator or tg_id in cfg.bot.admin_ids:
					await context.set_state(self)
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


		@router.callback_query(AdministrationForm.admin)
		async def test(call: CallbackQuery, state: FSMContext):
			if await utils.throttling_assert(state, count=5): return
			async with ChatActionSender.upload_video_note(chat_id=call.message.chat.id, bot=self.bot.tg):
							video_note = FSInputFile("media/video/415-base.mp4")
							await call.message.answer_video_note(video_note)
							await call.answer()
