import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart
from aiogram.utils.chat_action import ChatActionSender
from aiogram.methods.send_video_note import SendVideoNote


from omsu_bot.data.constants import greeting_message, user_agreement_message, callback_data_group, list_group
from omsu_bot.database.models import Student, User
from omsu_bot.handlers import Handler
from omsu_bot.keyboards.inline_user import super_inline_button, agree_inline_button, choice_a_role_inline_keyboard, \
	choice_a_course_inline_keyboard, group_inline_keyboard, yes_or_back_inline_keyboard
from omsu_bot.states.registration_states import RegisterFrom

import sqlalchemy as sa
import sqlalchemy.orm as sorm

class Registration(Handler):
	def __init__(self) -> None:
		super().__init__()

		router = Router()
		self.router = router

		@router.message(CommandStart())
		async def handle_start(message: Message, state: FSMContext) -> None:
			get_state = await state.get_state()

			if get_state is not None:
				data = await state.get_data()
				msg = data.get("get_msg")
				if msg is not None:
					await message.bot.delete_message(message.chat.id, msg.message_id)
				await state.clear()

			sess: sorm.Session = self.bot.db.session
			with sess.begin():
				res: sa.CursorResult = sess.execute(sa.select(User).where(User.tg_id == message.from_user.id))
				user: User = res.scalar_one_or_none()

			if user is None:
				msg = await message.answer(greeting_message, reply_markup=super_inline_button)
				await state.update_data(get_msg=msg)
				await state.set_state(RegisterFrom.get_super)
			else:
				await message.answer("Чем могу помочь?") #, reply_markup=menu_keyboard(message.from_user.id))
				pass

		@router.callback_query(RegisterFrom.get_super, F.data == "super")
		async def on_super(call: CallbackQuery, state: FSMContext) -> None:
			await state.set_state(RegisterFrom.get_agree)
			await call.message.edit_text(user_agreement_message, reply_markup=agree_inline_button)

		@router.callback_query(RegisterFrom.get_agree, F.data == "agree")
		async def on_agree(call: CallbackQuery, state: FSMContext) -> None:
			await state.set_state(RegisterFrom.get_role)
			await call.message.edit_text("Для начала вам нужно зарегистрироваться.\n\nВыберите роль:",
										reply_markup=choice_a_role_inline_keyboard)

		@router.callback_query(RegisterFrom.get_role, F.data.in_({"student", "teacher"}))
		async def on_role_select(call: CallbackQuery, state: FSMContext) -> None:
			select_role = call.data

			if select_role == "student":
				await state.update_data(role_id=select_role)
				await call.message.edit_text("Выберите курс:", reply_markup=choice_a_course_inline_keyboard)
				await state.set_state(RegisterFrom.get_course)
			elif select_role == "teacher":
				await call.message.answer("В разработке...")
				await call.answer()
				
		@router.callback_query(RegisterFrom.get_course, F.data.startswith("course_"))
		async def on_course_select(call: CallbackQuery, state: FSMContext) -> None:
			try:
				course_number = int(call.data.split("_")[1])
				await state.update_data(course_number=course_number)
				await call.message.edit_text("Выберите группу:", reply_markup=group_inline_keyboard(course_number))
				await state.set_state(RegisterFrom.get_group)
			except:
				await call.message.edit_text("Ошибка! Что-то пошло не так...")

		@router.callback_query(RegisterFrom.get_group, F.data.startswith("group_"))
		async def on_group_select(call: CallbackQuery, state: FSMContext) -> None:
			try:
				spl = call.data.split("_")
				group_id = int(spl[1])
				group_name = spl[2]

				await state.update_data(group_id=group_id)
				data = await state.get_data()
				course = data["course"]
				await call.message.edit_text(f"Курс: {course}\nГруппа: {group_name}\n\nВсе верно?",
											reply_markup=yes_or_back_inline_keyboard)
			except:
				await call.message.edit_text("Ошибка! Что-то пошло не так...")

		@router.callback_query(F.data == "yes")
		async def on_data_confirm(call: CallbackQuery, state: FSMContext) -> None:
			await call.message.delete()

			data = await state.get_data()
			role_id = data.get("role_id", None)
			course = data.get("course", None)
			group_id = data.get("group_id", None)

			await state.clear()

			success = False

			if True:
				tg_id = call.from_user.id
				sess: sorm.Session = self.bot.db.session
				with sess.begin():
					if sess.execute(sa.select(User).where(User.tg_id == tg_id)).first() is None:
						pk = sess.execute(sa.insert(User).values(tg_id=tg_id, role_id=role_id)).inserted_primary_key
						if pk:
							student = Student(user_id=pk[0], course_number=course, group_id=group_id)
							sess.add(student)
							success = True

			if success:
				await call.message.answer("Отлично! Вы успешно зарегистрированы. Приятного пользования!")
										#reply_markup=menu_keyboard(call.from_user.id)
			else:
				await call.message.answer("При регистрации возникла ошибка...") #, reply_markup=menu_keyboard(call.from_user.id))
				async with ChatActionSender.upload_video_note(chat_id=call.message.chat.id, bot=self.bot.tg):
					video_note = FSInputFile("media/video/cat-huh.mp4")
					await call.message.answer_video_note(video_note)

		@router.callback_query(RegisterFrom.get_course, RegisterFrom.get_group, F.data.startswith('back_'))
		async def process_back(call: CallbackQuery, state: FSMContext) -> None:
			data = call.data

			if data == "back_course":
				await state.set_state(RegisterFrom.get_role)
				await call.message.edit_text("Для начала вам нужно зарегистрироваться.\n\nВыберите роль:",
											reply_markup=choice_a_role_inline_keyboard)
			elif data == "back_group":
				await state.set_state(RegisterFrom.get_course)
				await call.message.edit_text("Выберите курс:", reply_markup=choice_a_course_inline_keyboard)

	async def enable(self, bot):
		await super().enable(bot)
		bot.dispatcher.include_router(self.router)

	