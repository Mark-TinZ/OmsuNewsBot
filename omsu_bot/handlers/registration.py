import json
import logging
import sqlalchemy as sa
import sqlalchemy.orm as sorm

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from omsu_bot import utils
import omsu_bot.data.language as lang
from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import RouterHandler, admin
from omsu_bot.handlers import groups
from omsu_bot.handlers.menu import MenuForm
from omsu_bot.database.models import Student, Teacher, User, Group

logger = logging.getLogger(__name__)


class RegistrationForm(StatesGroup):
	greetings_approval = HandlerState(
		text=lang.user_greetings,
		parse_mode="HTML",
		reply_markup=
			InlineKeyboardBuilder()
				.button(text="Продолжить", callback_data="approve")
				.as_markup()
	)
	
	warning_approval = HandlerState(
		text=lang.user_registration_warning,
		reply_markup=
			InlineKeyboardBuilder()
				.button(text="Принять", callback_data="approve")
				.as_markup()
	)

	role_selection = HandlerState(
		text=(
			"📝 Для начала вам нужно зарегистрироваться...\n\n"
			"Выберите *роль*:"
		),
		reply_markup=
			InlineKeyboardBuilder()
				.button(text="👨‍🎓 Студент", callback_data="student")
				.button(text="👨‍🏫 Преподаватель", callback_data="teacher")
				.adjust(2)
				.as_markup()
	)

	### TEACHER REGISTRATION ###
	teacher_auth = HandlerState(
		text=(
			"👨‍🏫 *Преподаватель*\n\nОтправьте сообщением ваш *ключ авторизации*:"
		),
		reply_markup=
			InlineKeyboardBuilder()
				.button(text="Отмена", callback_data="return")
				.as_markup()
	)

	async def teacher_approval_message(self, bot, state: FSMContext):
		await state.set_state(self)
		data = await state.get_data()
		return dict(
			text=f"👨‍🏫 *Преподаватель*\n*{data['teacher_name']}*\n\nПодтвердите, что *это вы*",
			reply_markup=InlineKeyboardBuilder()
				.button(text="Изменить ключ", callback_data="change")
				.button(text="Подтвердить", callback_data="confirm")
				.as_markup()
		)

	teacher_approval = HandlerState(message_handler=teacher_approval_message)

	### STUDENT REGISTRATION ###
	@staticmethod
	async def data_approval_message(self, bot, state: FSMContext):
		await state.set_state(self)
		data = await state.get_data()
		course_number = data["groups_course_number"]
		group_name = data["groups_group_name"]

		return dict(
			text=f"👨‍🎓 *Студент*\n📚 *Курс №{course_number}*\n💼 *Группа: {group_name}*\n\nВсё верно?",
			reply_markup=
				InlineKeyboardBuilder()
				.button(text="Изменить", callback_data="change")
				.button(text="Подтвердить", callback_data="confirm")
				.adjust(2)
				.as_markup()
		)

	data_approval = HandlerState(message_handler=data_approval_message)


class Registration(RouterHandler):
	def __init__(self) -> None:
		super().__init__()
		
		router: Router = self.router

		@router.message(CommandStart())
		async def handle_start(msg: Message, state: FSMContext) -> None:
			if await utils.throttling_assert(state): return
			
			if not self.bot.db.is_online():
				await state.clear()
				await msg.answer(text=lang.user_error_database_connection)
				return

			sender = msg.from_user

			sess: sorm.Session = self.bot.db.session

			if sess:
				with sess.begin():
					user: User = sess.execute(sa.select(User).where(User.tg_id == sender.id)).scalar_one_or_none()

			if user:
				await MenuForm.menu_main.message_send(self.bot, state, msg.chat, msg.message_id)
			else:
				await RegistrationForm.greetings_approval.message_send(self.bot, state, msg.chat, msg.message_id)
		
		@router.callback_query(RegistrationForm.greetings_approval)
		async def handle_greetings_approval(call: CallbackQuery, state: FSMContext):
			if call.data == "approve":
				await call.answer()
				await RegistrationForm.warning_approval.message_edit(self.bot, state, call.message)

		@router.callback_query(RegistrationForm.warning_approval)
		async def handle_eula_approval(call: CallbackQuery, state: FSMContext):
			if call.data == "approve":
				await call.answer()
				await RegistrationForm.role_selection.message_edit(self.bot, state, call.message)

		@router.callback_query(RegistrationForm.role_selection)
		async def handle_role_selection(call: CallbackQuery, state: FSMContext):
			if await utils.throttling_assert(state): return
			
			await call.answer()

			match call.data:
				case "student":
					await groups.GroupsForm.course_selection.message_edit(self.bot, state, call.message, title="*👨‍🎓 Студент*", prev_state=RegistrationForm.role_selection, next_state=RegistrationForm.data_approval)
				case "teacher":
					await RegistrationForm.teacher_auth.message_edit(self.bot, state, call.message)
		
		@router.callback_query(RegistrationForm.teacher_auth)
		async def handle_teacher_auth_call(call: CallbackQuery, state: FSMContext):
			if await utils.throttling_assert(state): return
			
			await call.answer()
			
			if call.data == "return":
				await RegistrationForm.role_selection.message_edit(self.bot, state, call.message)
				return
		
		@router.message(RegistrationForm.teacher_auth)
		async def handle_teacher_auth(msg: Message, state: FSMContext):
			if await utils.throttling_assert(state, count=1, freq=3.0): return
			
			if not msg.text:
				return

			if not self.bot.db.is_online():
				logger.error(f"id={msg.from_user.id}, {lang.user_error_database_connection}")
				await msg.answer(text=lang.user_error_database_connection)
				return

			success = False
			tg_id = msg.from_user.id
			sess: sorm.Session = self.bot.db.session
			with sess.begin():
				teacher = sess.execute(sa.select(Teacher).where(Teacher.tg_authkey == msg.text, Teacher.user_id == sa.null())).scalar_one_or_none()

				if teacher:
					name = teacher.name
					success = True
			
			if success:
				await state.update_data(teacher_name=name, teacher_authkey=msg.text)
				await RegistrationForm.teacher_approval.message_send(self.bot, state, chat=msg.chat, reply_to_message_id=msg.message_id)
			else:
				logger.error(f"id={msg.from_user.id}, *Преподаватель* При регистрации возникла ошибка... *несуществующий ключ авторизации*")
				await msg.answer_video_note(FSInputFile("media/video/cat-huh.mp4"))
				ans = await msg.answer(
					text="👨‍🏫 *Преподаватель*\n\n*При регистрации возникла ошибка...*\nВозможно вы ввели *несуществующий ключ авторизации*\nПроверьте и отправьте ключ ещё раз",
					parse_mode="Markdown",
					reply_markup=RegistrationForm.teacher_auth.reply_markup
				)
				await utils.register_context(state, ans)

		@router.callback_query(RegistrationForm.teacher_approval)
		async def handle_teacher_approval(call: CallbackQuery, state: FSMContext):
			if await utils.throttling_assert(state): return

			await call.answer()

			c = call.data
			if c == "change":
				await RegistrationForm.teacher_auth.message_edit(self.bot, state, call.message)
				return
			
			if c != "confirm":
				return

			if not self.bot. db.is_online():
				logger.error(f"id={call.message.from_user.id}, {lang.user_error_database_connection}")
				await call.message.edit_text(text=lang.user_error_database_connection)
				return

			data = await state.get_data()
			authkey = data["teacher_authkey"]
			name = data["teacher_name"]

			tg_id = call.from_user.id
			success = False
			sess: sorm.Session = self.bot.db.session
			with sess.begin():
				teacher = sess.execute(sa.select(Teacher).where(Teacher.tg_authkey == authkey, Teacher.user_id == sa.null(), Teacher.name == name)).scalar_one_or_none()

				if teacher:
					settings_dict: dict = dict()
					settings_dict["notifications_enable"] = True
					settings_dict["schedule_view"] = False
					settings_json = json.dumps(settings_dict)
					pk = sess.execute(sa.insert(User).values(tg_id=tg_id, role_id="teacher", settings=settings_json)).inserted_primary_key
					if pk:
						teacher.user_id = pk[0]
						success = True
			
			if success:
				await state.clear()
				await call.message.edit_text(
					text=f"👨‍🏫 *Преподаватель*\n*{name}*\n\nВы успешно зарегистрированы!\n\nИспользуйте /start для взаимодействия",
					parse_mode="Markdown"
				)
			else:
				logger.error(f"id={call.message.from_user.id}, *Преподаватель* При регистрации возникла ошибка... *ключ уже недействителен*")
				await call.message.edit_text(
					text="👨‍🏫 *Преподаватель*\n\n*При регистрации возникла ошибка...*\nВозможно этот *ключ уже недействителен*\nПроверьте и отправьте ключ ещё раз",
					parse_mode="Markdown",
					reply_markup=RegistrationForm.teacher_auth.reply_markup
				)
				async with ChatActionSender.upload_video_note(chat_id=call.chat.id, bot=self.bot.tg):
					video_note = FSInputFile("media/video/cat-huh.mp4")
					await call.message.answer_video_note(video_note)	

		@router.callback_query(RegistrationForm.data_approval)
		async def handle_data_approval(call: CallbackQuery, state: FSMContext):
			if await utils.throttling_assert(state): return
			
			await call.answer()
			c = call.data
			if c == "change":
				await groups.GroupsForm.course_selection.message_edit(self.bot, state, call.message, title="*👨‍🎓 Студент*", prev_state=RegistrationForm.role_selection, next_state=RegistrationForm.data_approval)
				return
			
			if c != "confirm":
				return
			
			## approved ##

			if not self.bot.db.is_online():
				logger.error(f"id={call.message.from_user.id}, {lang.user_error_database_connection}")
				await call.message.edit_text(text=lang.user_error_database_connection)
				return
			
			data = await state.get_data()
			group_id = data["groups_group_id"]
			group_name = data["groups_group_name"]
			course_number = data["groups_course_number"]

			await state.clear()

			success = False

			tg_id = call.from_user.id
			sess: sorm.Session = self.bot.db.session
			with sess.begin():
				group: Group | None  = sess.execute(sa.select(Group).where(Group.id_ == group_id, Group.is_enabled == True)).scalar_one_or_none()
				if group:
					settings_dict: dict = dict()
					settings_dict["notifications_enabled"] = True
					settings_dict["schedule_view"] = False
					settings_json = json.dumps(settings_dict)
					pk = sess.execute(sa.insert(User).values(tg_id=tg_id, role_id="student", settings=settings_json)).inserted_primary_key
					if pk:
						student = Student(user_id=pk[0], group_id=group_id)
						sess.add(student)
						success = True

			if success:
				await call.message.edit_text(
					text=f"👨‍🎓 *Студент*\n📚 *Курс №{course_number}*\n💼 *Группа: {group_name}*\n\nВы успешно зарегистрированы!\n\nИспользуйте /start для взаимодействия",
					parse_mode="Markdown"
				)
			else:
				logger.error(f"id={call.message.from_user.id}, При регистрации возникла ошибка...")
				await call.message.edit_text("При регистрации возникла ошибка...")
				await call.message.answer_video_note(FSInputFile("media/video/error-bd.mp4"))
		



	
