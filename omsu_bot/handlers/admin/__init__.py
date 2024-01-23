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
from omsu_bot.database.models import Group, User, Student, Teacher

logger = logging.getLogger(__name__)


class AdministrationForm(StatesGroup):
	# @staticmethod
	# async def admin_message(self, bot, context: FSMContext):
	# 	tg_id = context.key.user_id
	# 	if tg_id in bot.config.admin_ids:
	# 		return dict(
	# 			text=lang.user_admin_description,
	# 			reply_markup=
	# 				InlineKeyboardBuilder()
	# 				.button(text="Расписание", callback_data="admin_schedule")
	# 				.as_markup(),
	# 			register_context=True
	# 		)

	# 	if not bot.db.is_online(): return dict(text=lang.user_error_database_connection)

	# 	sess: sorm.Session = bot.db.session

	# 	with sess.begin():
	# 		user: User | None = sess.execute(sa.select(User).where(User.tg_id == tg_id)).scalar_one_or_none()

	# 		if not user:
	# 			logger.info(f"tg_id={tg_id} не зарегистрирован!")
	# 			return dict(text=lang.user_error_auth_unknown)

	# 		if user.role_id == "student":
	# 			union = sess.execute(
	# 				sa.select(Student, Group)
	# 				.where(Student.user_id == user.id_)
	# 				.join(Group, Student.group_id == Group.id_)
	# 			).first()

	# 			if not union or len(union) != 2:
	# 				logger.error(f"tg_id={tg_id}, user_id={user.id_} отсуствует запись student или group!")
	# 				return dict(text=lang.user_error_database_logic)

	# 			student, group = union

	# 			if student.is_moderator:
	# 				await context.set_state(self)
	# 				return dict(
	# 					text=lang.user_admin_description,
	# 					reply_markup=
	# 						InlineKeyboardBuilder()
	# 						.button(text=group.name, callback_data="schedule")
	# 						.as_markup(),
	# 					register_context=True
	# 				)
				
	# 			return None
	

	admin = HandlerState(
		text="*🛠️ Админ-меню*\n\n",
		reply_markup=
			InlineKeyboardBuilder()
				.button(text="💼 Группы", callback_data="admin_groups")
				.button(text="👨‍🎓 Пользователи", callback_data="admin_users")
				.as_markup()
	)


	@staticmethod
	async def schedule_message(self, bot, context: FSMContext):
		pass



class Administration(RouterHandler):
	def __init__(self):
		super().__init__()
		
		router: Router = self.router


		@router.callback_query(AdministrationForm.admin)
		async def handle_admin(call: CallbackQuery, state: FSMContext):
			if await utils.throttling_assert(state, count=5): return
			await call.message.answer_video_note(FSInputFile("media/video/415-base.mp4"))
			await call.answer()
