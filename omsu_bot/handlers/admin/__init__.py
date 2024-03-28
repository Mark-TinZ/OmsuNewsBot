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
import omsu_bot.data.lang as lang
from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import groups
from omsu_bot.handlers import RouterHandler
from omsu_bot.database.models import Group, User, Student, Teacher

logger = logging.getLogger(__name__)


class AdminForm(StatesGroup):
	admin = HandlerState(
		text="*🛠️ Админ-меню*\n\n",
		reply_markup=
			InlineKeyboardBuilder()
				.button(text="💼 Группы", callback_data="admin_groups")
				.button(text="👨‍🎓 Пользователи", callback_data="admin_users")
				.as_markup()
	)


	


	@staticmethod
	async def group_settings_message(self, bot, context: FSMContext):
		if not bot.db.is_online(): return dict(text=lang.user_error_database_connection)

		data = await context.get_data()

		tg_id = context.key.user_id

		group_id = data.get("groups_group_id", None)
		if not group_id: return dict(text="Ошибочка...")

		sess: sorm.Session = bot.db.session

		builder = (InlineKeyboardBuilder()
			.button(text="Расписание", callback_data="group_schedule")
		)

		with sess.begin():
			group: Group = sess.execute(sa.Select(Group).where(Group.id_ == group_id)).scalar_one_or_none()
			group_course = group.course_number
			group_name = group.name
			student_count: int = sess.execute(sa.Select(sa.func.count(Student.id_)).where(Student.group_id == group_id)).scalar()


		if tg_id in bot.config.main.admin_ids:
			pass
		
		return dict(
			text=f"*💼 Группа:* {group_name}\n\n📚 *Курс №{group_course}*\n👨‍🎓 *Кол-во студентов:* {student_count}",
			reply_markup=builder.as_markup()
		)

	group_settings = HandlerState(
		message_handler=group_settings_message
	)


	@staticmethod
	async def schedule_message(self, bot, context: FSMContext) -> None:
		pass




class Admin(RouterHandler):
	def __init__(self) -> None:
		super().__init__()
		
		router: Router = self.router


		@router.callback_query(AdminForm.admin)
		async def handle_admin(call: CallbackQuery, state: FSMContext) -> None:
			if await utils.throttling_assert(state, count=5): return
			tg_id = call.from_user.id
			
			if tg_id not in self.bot.config.main.admin_ids: return

			match call.data:
				case "admin_groups":
					await groups.GroupsForm.course_selection.message_edit(
						self.bot, 
						state, 
						call.message, 
						title="*👨‍🎓 Студент*", 
						prev_state=AdminForm.admin, 
						next_state=AdminForm.group_settings
					)
				case "admin_users":
					pass
				case _:
					await call.message.answer_video_note(FSInputFile("media/video/415-base.mp4"))
			await call.answer()
