import logging

import sqlalchemy as sa
import sqlalchemy.orm as sorm

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

import omsu_bot.data.language as lang
from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import RouterHandler
from omsu_bot.database.models import Student, Teacher, User, Group


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


	async def teacher_approval_message(bot, state: FSMContext):
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

	course_selection = HandlerState(
		text=(
			"👨‍🎓 *Студент*\n\nВыберите *курс* обучения:"
		),
		reply_markup=
			InlineKeyboardBuilder()
				.button(text="Курс №1", callback_data="1")
				.button(text="Курс №2", callback_data="2")
				.button(text="Курс №3", callback_data="3")
				.button(text="Курс №4", callback_data="4")
				.adjust(2)
				.row(InlineKeyboardButton(text="Назад", callback_data="return"))
				.as_markup(),
		previous_state=role_selection
	)

	@staticmethod
	async def group_selection_message(bot, state: FSMContext):
		if not bot.db.is_online():
			return dict(
				text=lang.user_error_database_connection
			)

		data = await state.get_data()
		course_number = data["course_number"]

		
		sess: sorm.Session = bot.db.session
		
		with sess.begin():
			res: sa.ScalarResult = sess.execute(sa.select(Group).where(Group.course_number == course_number, Group.is_enabled == True)).scalars()

		builder = InlineKeyboardBuilder()
		for group in res:
			builder.button(text=group.name, callback_data=f"{group.id_}/{group.name}")

		builder.adjust(2)
		builder.row(InlineKeyboardButton(text="Назад", callback_data="return"))

		return dict(
			text=f"👨‍🎓 *Студент*\n📚 *Курс №{course_number}*\n\nВыберите *группу*:",
			reply_markup=builder.as_markup()
		)

	group_selection = HandlerState(message_handler=group_selection_message, previous_state=course_selection)


	@staticmethod
	async def data_approval_message(bot, state: FSMContext):
		data = await state.get_data()
		course_number = data["course_number"]
		group_name = data["group_name"]

		return dict(
			text=f"👨‍🎓 *Студент*\n📚 *Курс №{course_number}*\n💼 *Группа: {group_name}*\n\nВсё верно?",
			reply_markup=
				InlineKeyboardBuilder()
				.button(text="Изменить", callback_data="change")
				.button(text="Подтвердить", callback_data="confirm")
				.adjust(2)
				.as_markup()
		)

	data_approval = HandlerState(message_handler=data_approval_message, previous_state=group_selection)


	




class Registration(RouterHandler):
	def __init__(self) -> None:
		super().__init__()
		
		router: Router = self.router

		@router.message(CommandStart())
		async def handle_start(msg: Message, state: FSMContext) -> None:
			async with ChatActionSender.typing(chat_id=msg.chat.id, bot=self.bot.tg):
				sess: sorm.Session = self.bot.db.session

				if sess:
					with sess.begin():
						user: User = sess.execute(sa.select(User).where(User.tg_id == msg.from_user.id)).scalar_one_or_none()
				else:
					await state.clear()
					await msg.answer(text=lang.user_error_database_connection)
					return

				if user:
					await msg.answer("Чем могу помочь?")
				else:
					await RegistrationForm.greetings_approval.message_send(self.bot, state, msg.chat, msg.message_id)
		
		@router.callback_query(RegistrationForm.greetings_approval)
		async def handle_greetings_approval(call: CallbackQuery, state: FSMContext):
			if call.data == "approve":
				await RegistrationForm.warning_approval.message_edit(self.bot, state, call.message)
		

		@router.callback_query(RegistrationForm.warning_approval)
		async def handle_eula_approval(call: CallbackQuery, state: FSMContext):
			if call.data == "approve":
				await RegistrationForm.role_selection.message_edit(self.bot, state, call.message)
		

		@router.callback_query(RegistrationForm.role_selection)
		async def handle_role_selection(call: CallbackQuery, state: FSMContext):
			match call.data:
				case "student":
					await RegistrationForm.course_selection.message_edit(self.bot, state, call.message)
				case "teacher":
					await RegistrationForm.teacher_auth.message_edit(self.bot, state, call.message)
				case _:
					await call.answer("В процессе разработки")
		
		@router.callback_query(RegistrationForm.teacher_auth)
		async def handle_teacher_auth_call(call: CallbackQuery, state: FSMContext):
			if call.data == "return":
				await RegistrationForm.role_selection.message_edit(self.bot, state, call.message)
				return
		
		@router.message(RegistrationForm.teacher_auth)
		async def handle_teacher_auth(msg: Message, state: FSMContext):
			if not msg.text:
				return

			if not self.bot.db.is_online():
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
				await msg.answer(
					text="👨‍🏫 *Преподаватель*\n\n*При регистрации возникла ошибка...*\nВозможно вы ввели *несуществующий ключ авторизации*\nПроверьте и отправьте ключ ещё раз",
					parse_mode="Markdown",
					reply_markup=RegistrationForm.teacher_auth.reply_markup
				)
				async with ChatActionSender.upload_video_note(chat_id=msg.chat.id, bot=self.bot.tg):
					video_note = FSInputFile("media/video/cat-huh.mp4")
					await msg.answer_video_note(video_note)
		

		@router.callback_query(RegistrationForm.teacher_approval)
		async def handle_teacher_approval(call: CallbackQuery, state: FSMContext):
			c = call.data
			if c == "change":
				await RegistrationForm.teacher_auth.message_edit(self.bot, state, call.message)
				return
			
			if c != "confirm":
				return

			if not self.bot.db.is_online():
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
					pk = sess.execute(sa.insert(User).values(tg_id=tg_id, role_id="teacher")).inserted_primary_key
					if pk:
						teacher.user_id = pk[0]
						success = True
			
			if success:
				await state.clear()
				await call.message.edit_text(
					text=f"👨‍🏫 *Преподаватель*\n*{name}*\n\nВы успешно зарегистрированы!",
					parse_mode="Markdown"
				)
			else:
				await call.message.edit_text(
					text="👨‍🏫 *Преподаватель*\n\n*При регистрации возникла ошибка...*\nВозможно этот *ключ уже недействителен*\nПроверьте и отправьте ключ ещё раз",
					parse_mode="Markdown",
					reply_markup=RegistrationForm.teacher_auth.reply_markup
				)
				async with ChatActionSender.upload_video_note(chat_id=call.chat.id, bot=self.bot.tg):
					video_note = FSInputFile("media/video/cat-huh.mp4")
					await call.message.answer_video_note(video_note)
			



		@router.callback_query(RegistrationForm.course_selection)
		async def handle_course_selection(call: CallbackQuery, state: FSMContext):
			if call.data == "return":
				await RegistrationForm.role_selection.message_edit(self.bot, state, call.message)
				return
			
			async with ChatActionSender.typing(chat_id=call.message.chat.id, bot=self.bot.tg):
				if not call.data.isdigit():
					return
				
				course_number = int(call.data)
				await state.update_data(course_number=course_number)
				await RegistrationForm.group_selection.message_edit(self.bot, state, call.message)
		
		
		@router.callback_query(RegistrationForm.group_selection)
		async def handle_group_selection(call: CallbackQuery, state: FSMContext):
			if call.data == "return":
				await RegistrationForm.course_selection.message_edit(self.bot, state, call.message)
				return
			
			c = call.data
			try:
				spl: int = c.find("/")
				group_id: int = int(c[:spl])
				group_name: str = c[(spl+1):]
			except:
				return
			
			await state.update_data(group_id=group_id, group_name=group_name)

			await RegistrationForm.data_approval.message_edit(self.bot, state, call.message)
		

		@router.callback_query(RegistrationForm.data_approval)
		async def handle_data_approval(call: CallbackQuery, state: FSMContext):
			async with ChatActionSender.typing(chat_id=call.message.chat.id, bot=self.bot.tg):
				c = call.data

				if c == "change":
					await RegistrationForm.course_selection.message_edit(self.bot, state, call.message)
					return
				
				if c != "confirm":
					return
				
				## approved ##

				if not self.bot.db.is_online():
					await call.message.edit_text(text=lang.user_error_database_connection)
					return
				
				data = await state.get_data()
				group_id = data["group_id"]
				group_name = data["group_name"]
				course_number = data["course_number"]

				await state.clear()

				success = False

				tg_id = call.from_user.id
				sess: sorm.Session = self.bot.db.session
				with sess.begin():
					group = sess.execute(sa.select(Group).where(Group.id_ == group_id, Group.is_enabled == True)).scalar_one_or_none()
					if group:
						pk = sess.execute(sa.insert(User).values(tg_id=tg_id, role_id="student")).inserted_primary_key
						if pk:
							student = Student(user_id=pk[0], group_id=group_id)
							sess.add(student)
							success = True
				
				if success:
					await call.message.edit_text(
						text=f"👨‍🎓 *Студент*\n📚 *Курс №{course_number}*\n💼 *Группа: {group_name}*\n\nВы успешно зарегистрированы!",
						parse_mode="Markdown"
					)
				else:
					await call.message.edit_text("При регистрации возникла ошибка...")
					async with ChatActionSender.upload_video_note(chat_id=call.message.chat.id, bot=self.bot.tg):
						video_note = FSInputFile("media/video/cat-huh.mp4")
						await call.message.answer_video_note(video_note)
		

		# @router.message(CommandStart())
		# async def handle_start(message: Message, state: FSMContext) -> None:
		# 	get_state = await state.get_state()

		# 	if get_state is not None:
		# 		data = await state.get_data()
		# 		msg = data.get("get_msg")
		# 		if msg is not None:
		# 			await message.bot.delete_message(message.chat.id, msg.message_id)
		# 		await state.clear()

		# 	sess: sorm.Session = self.bot.db.session
		# 	with sess.begin():
		# 		user: User = sess.execute(sa.select(User).where(User.tg_id == message.from_user.id)).scalar_one_or_none()

		# 	if user is None:
		# 		msg = await message.answer(greeting_message, reply_markup=super_inline_button)
		# 		await state.update_data(get_msg=msg)
		# 		await state.set_state(RegisterForm.get_super)
		# 	else:
		# 		await message.answer("Чем могу помочь?") #, reply_markup=menu_keyboard(message.from_user.id))
		# 		pass

		# @router.callback_query(RegisterForm.get_super, F.data == "super")
		# async def on_super(call: CallbackQuery, state: FSMContext) -> None:
		# 	await state.set_state(RegisterForm.get_agree)
		# 	await call.message.edit_text(user_agreement_message, reply_markup=agree_inline_button)

		# @router.callback_query(RegisterForm.get_agree, F.data == "agree")
		# async def on_agree(call: CallbackQuery, state: FSMContext) -> None:
		# 	await state.set_state(RegisterForm.get_role)
		# 	await call.message.edit_text("Для начала вам нужно зарегистрироваться.\n\nВыберите роль:",
		# 								reply_markup=choice_a_role_inline_keyboard)

		# @router.callback_query(RegisterForm.get_role, F.data.in_({"student", "teacher"}))
		# async def on_role_select(call: CallbackQuery, state: FSMContext) -> None:
		# 	select_role = call.data

		# 	if select_role == "student":
		# 		await call.message.edit_text("Выберите курс:", reply_markup=choice_a_course_inline_keyboard)
		# 		await state.set_state(RegisterForm.get_course)
		# 	elif select_role == "teacher":
		# 		await state.clear()  # TODO: Затычка
		# 		await call.message.edit_text("В разработке...")
		# 		await call.answer()

		# @router.callback_query(RegisterForm.get_course, F.data.startswith("course_"))
		# async def student_course_selected(call: CallbackQuery, state: FSMContext) -> None:
			# course_number = int(call.data.split("_")[1])
			# await state.update_data(course_number=course_number)

			# sess: sorm.Session = self.bot.db.session
			
			# with sess.begin():
			# 	res: sa.ScalarResult = sess.execute(sa.select(Group).where(Group.course_number == course_number)).scalars()
			# groups = [(group.name, group.id_) for group in res]

			# await call.message.edit_text("Выберите группу:", reply_markup=group_inline_keyboard(groups))
			# await state.set_state(RegisterForm.get_group)


		# @router.callback_query(RegisterForm.get_group, F.data.startswith("group_"))
		# async def student_group_selected(call: CallbackQuery, state: FSMContext) -> None:
		# 	try:
		# 		spl = call.data.split("_")
		# 		group_id = int(spl[1])
		# 		group_name = spl[2]
		# 	except Exception as e:
		# 		await call.message.edit_text("При регистрации возникла ошибка...")
		# 		async with ChatActionSender.upload_video_note(chat_id=call.message.chat.id, bot=self.bot.tg):
		# 			video_note = FSInputFile("media/video/cat-huh.mp4")
		# 			await call.message.answer_video_note(video_note)
		# 		logging.error(e)
		# 		return

		# 	await state.update_data(group_id=group_id)
		# 	data = await state.get_data()
		# 	course = data["course_number"]
		# 	await call.message.edit_text(f"Курс: {course}\nГруппа: {group_name}\n\nВсе верно?",
		# 								reply_markup=yes_or_back_inline_keyboard)

		# @router.callback_query(F.data == "yes")
		# async def student_data_confirmed(call: CallbackQuery, state: FSMContext) -> None:
		# 	# await call.message.delete()

			# data = await state.get_data()
			# group_id = data.get("group_id", None)

			# await state.clear()

			# success = False

			# tg_id = call.from_user.id
			# sess: sorm.Session = self.bot.db.session
			# with sess.begin():
			# 	pk = sess.execute(sa.insert(User).values(tg_id=tg_id, role_id="student")).inserted_primary_key
			# 	if pk:
			# 		student = Student(user_id=pk[0], group_id=group_id)
			# 		sess.add(student)
			# 		success = True

		# 	if success:
		# 		await call.message.edit_text("Отлично! Вы успешно зарегистрированы. Приятного пользования!")
		# 	else:
		# 		await call.message.edit_text("При регистрации возникла ошибка...") #, reply_markup=menu_keyboard(call.from_user.id))
		# 		async with ChatActionSender.upload_video_note(chat_id=call.message.chat.id, bot=self.bot.tg):
		# 			video_note = FSInputFile("media/video/cat-huh.mp4")
		# 			await call.message.answer_video_note(video_note)

		# @router.callback_query(F.data.startswith('back_'))
		# async def process_back(call: CallbackQuery, state: FSMContext) -> None:
		# 	data = call.data
			
		# 	match data:
		# 		case "back_course":
		# 			pass


	
