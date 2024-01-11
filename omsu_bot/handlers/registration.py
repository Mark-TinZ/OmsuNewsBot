import logging
from shutil import which

import sqlalchemy as sa
import sqlalchemy.orm as sorm
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.keyboard import InlineKeyboardBuilder

import omsu_bot.data.constants as constants
from omsu_bot.database.models import Student, User, Group
from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import RouterHandler


class RegistrationForm(StatesGroup):
	
	greetings_approval = HandlerState(
		text=constants.greetings_message,
		parse_mode="HTML",
		reply_markup=
			InlineKeyboardBuilder()
				.button(text="Продолжить", callback_data="approve")
				.as_markup()
	)
	
	eula_approval = HandlerState(
		text=constants.user_eula_message,
		reply_markup=
			InlineKeyboardBuilder()
				.button(text="Принять", callback_data="approve")
				.as_markup()
	)

	role_selection = HandlerState(
		text=(
			"Для начала вам нужно зарегистрироваться...\n\n"
			"Выберите роль:"
		),
		reply_markup=
			InlineKeyboardBuilder()
				.button(text="👨‍🎓 Студент", callback_data="student")
				.button(text="👨‍🏫 Преподаватель", callback_data="teacher")
				.adjust(2)
				.as_markup()
	)


	### STUDENT REGISTRATION ###

	course_selection = HandlerState(
		text=(
			"Выберите курс обучения:"
		),
		reply_markup=
			InlineKeyboardBuilder()
				.button(text="Курс №1", callback_data="1")
				.button(text="Курс №2", callback_data="2")
				.button(text="Курс №3", callback_data="3")
				.button(text="Курс №4", callback_data="4")
				.adjust(2, repeat=True)
				.as_markup()
	)

	@staticmethod
	async def group_selection_message(bot, state: FSMContext):
		data = await state.get_data()
		course_number = data.course_number

		sess: sorm.Session = bot.db.session
		
		with sess.begin():
			res: sa.ScalarResult = sess.execute(sa.select(Group).where(Group.course_number == course_number)).scalars()

		builder = InlineKeyboardBuilder()
		for group in res:
			builder.button(text=group.name, callback_data=group.id_)

		builder.adjust(2, repeat=True)

		return dict(
			text=f"Курс №{course_number}\nВыберите группу:",
			reply_markup=builder.as_markup()
		)

	group_selection = HandlerState()


	@staticmethod
	async def data_approval_message(bot, state: FSMContext):
		data = await state.get_data()
		course_number = data.course_number
		group_name = data.group_name

		return dict(
			text=f"Курс №{course_number}\nГруппа: {group_name}\n\nВсё верно?",
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
		
		router = self.router

		@router.message(CommandStart())
		async def handle_start(msg: Message, state: FSMContext) -> None:
			async with ChatActionSender.typing(chat_id=msg.chat.id, bot=self.bot.tg):
				sess: sorm.Session = self.bot.db.session

				if sess:
					with sess.begin():
						user: User = sess.execute(sa.select(User).where(User.tg_id == msg.from_user.id)).scalar_one_or_none()
				else:
					await state.clear()
					await msg.answer("Error BD")
					return

				if user:
					await msg.answer("Чем могу помочь?")
				else:
					await RegistrationForm.greetings_approval.message_send(self.bot, state, msg.chat, msg.message_id)
		
		@router.callback_query(RegistrationForm.greetings_approval)
		async def handle_greetings_approval(call: CallbackQuery, state: FSMContext):
			RegistrationForm.role_selection.message_edit(self.bot, state, call.message)

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

		# 	data = await state.get_data()
		# 	group_id = data.get("group_id", None)

		# 	await state.clear()

		# 	success = False

		# 	tg_id = call.from_user.id
		# 	sess: sorm.Session = self.bot.db.session
		# 	with sess.begin():
		# 		pk = sess.execute(sa.insert(User).values(tg_id=tg_id, role_id="student")).inserted_primary_key
		# 		if pk:
		# 			student = Student(user_id=pk[0], group_id=group_id)
		# 			sess.add(student)
		# 			success = True

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


	
