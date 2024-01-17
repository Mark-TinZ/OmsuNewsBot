import sqlalchemy as sa
import sqlalchemy.orm as sorm

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from omsu_bot import utils
from omsu_bot.fsm import HandlerState
import omsu_bot.data.language as lang
from omsu_bot.handlers import RouterHandler
from omsu_bot.database.models import Student, Group, Teacher, User


class SettingsForm(StatesGroup):
	@staticmethod
	async def settings_message(self, bot, context: FSMContext):
		await context.set_state(self)

		if not bot.db.is_online():
			return dict(text=lang.user_error_database_connection)

		tg_id = context.key.user_id

		text = "⚙ *Настройки*\n\n"

		sess: sorm.Session = bot.db.session

		with sess.begin(): 
			user: User | None = sess.execute(sa.select(User).where(User.tg_id == tg_id)).scalar_one_or_none()

			if not user:
				return dict(text=lang.user_error_auth_unknown)

			if user.role_id == "student":
				union = sess.execute(
					sa.select(Student, Group)
					.where(Student.user_id == user.id_)
					.join(Group, Group.id_ == Student.group_id)
				).first()

				if not (union and union[0] and union[1]):
					return dict(text=lang.user_error_database_logic)

				student, group = union

				text += f"*👨‍🎓 Студент\n💼 Группа:* {group.name}"

			elif user.role_id == "teacher":
				teacher: Teacher = sess.execute(
					sa.select(Teacher)
					.where(Teacher.user_id == user.id_)
				).scalar_one_or_none()

				if not teacher:
					return dict(text=lang.user_error_database_logic)

				text += f"*👨‍🏫 Преподаватель\n😎 Имя:* {teacher.name}"
		

		return dict(
			text=text,
			reply_markup=self.reply_markup
		)

		

	settings = HandlerState(
		message_handler=settings_message,
		reply_markup=
			InlineKeyboardBuilder()
				.button(text="🔕/🔔 Беззвучный режим", callback_data="notifications_enable")
				.button(text="🖼/📄 Отображение рассписания", callback_data="schedule_view")
				.button(text="❌ Удалить аккаунт", callback_data="account_remove")
				.adjust(1)
				.as_markup()
	)


class Settings(RouterHandler):
	def __init__(self):
		super().__init__()
		
		router: Router = self.router

		@router.callback_query(SettingsForm.settings)
		async def handle_settings(call: CallbackQuery, state: FSMContext):
			if await utils.throttling_assert(state): return

			if not self.bot.db.is_online():
				await call.message.edit_text(text=lang.user_error_auth_unknown)
			
			
			sess: sorm.Session = self.bot.db.session

			actor = call.from_user

			match call.data:
				case "account_remove":
					await state.clear()
					with sess.begin():
						user = sess.execute(sa.select(User).where(User.tg_id == actor.id)).scalar_one_or_none()
						
						if not user:
							await call.message.edit_text(text=lang.user_error_auth_unknown)
							return
						
						if user.role_id == "student":
							sess.execute(sa.delete(Student).where(Student.user_id == user.id_))
						elif user.role_id == "teacher":
							sess.execute(sa.update(Teacher).where(Teacher.user_id == user.id_).values(user_id=sa.null()))
						
						sess.delete(user)
						
						await call.message.edit_text(
							text="⛔ Ваш аккаунт успешно *удалён*",
							parse_mode="Markdown"
						)
				case _:
					await call.answer(text="В разработке...")
						




		