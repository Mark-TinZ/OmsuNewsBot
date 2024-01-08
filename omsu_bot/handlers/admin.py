
from aiogram import Router, F

from aiogram.types import Message, CallbackQuery

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from omsu_bot.data.constants import description_admin_panel, callback_data_group, list_group
from omsu_bot.database.models import Student
from omsu_bot.handlers import Handler
from omsu_bot.keyboards.inline_admin import admin_menu_inline, moderator_menu_inline, weekday_inline_keyboard
from omsu_bot.keyboards.inline_user import choice_a_course_inline_keyboard, group_inline_keyboard
from omsu_bot.states.admin_states import SchedulesFrom

import sqlalchemy as sa
import sqlalchemy.orm as sorm



class SchedulesFrom(StatesGroup):
    get_course = State()
    get_group = State()
    get_weekday = State()
    get_pairs = State()


class Administration(Handler):
	router: Router = Router()
	async def enable(self, bot):
		await super().enable(bot)
		bot.dispatcher.include_router(self.router)

	@router.message(F.text == "Админ-панель")
	async def menu_admin(self, message: Message, state: FSMContext) -> None:
		await state.clear()

		sess: sorm.Session = self.bot.db.session
		with sess.begin():
			res: sa.CursorResult = sess.execute(sa.select(Student).where(Student.user_id == message.from_user.id))
			student: Student = res.scalar_one_or_none()

		if message.from_user.id in message.bot.config.tg_bot.admin_ids:
			await message.answer(f"<b>Админ-панель:</b> \n{description_admin_panel}", reply_markup=admin_menu_inline)
		elif student.is_moderator:
			await message.answer(f"<b>Админ-панель:</b> \n{description_admin_panel}", reply_markup=moderator_menu_inline)

	@router.callback_query(F.data == "edit_schedules")
	async def edit_schedule(self, call: CallbackQuery, state: FSMContext) -> None:
		if call.from_user.id in call.bot.config.tg_bot.admin_ids:
			await state.set_state(SchedulesFrom.get_course)
			await call.message.edit_text("Выберите курс:", reply_markup=choice_a_course_inline_keyboard)

	@router.callback_query(SchedulesFrom.get_course, F.data.startswith("course_"))
	async def get_course(self, call: CallbackQuery, state: FSMContext) -> None:
		course = call.data.split("_")[1]
		await state.update_data(course=course)
		await state.set_state(SchedulesFrom.get_group)
		await call.message.edit_text("Выберите группу:", reply_markup=group_inline_keyboard(course))

	@router.callback_query(SchedulesFrom.get_group, F.data.startswith("group_"))
	async def get_group(self, call: CallbackQuery, state: FSMContext) -> None:
		data = await state.get_data()

		for key, val in enumerate(callback_data_group[data['course']]):
			if val.startswith(call.data):
				group = list_group[data['course']][key]
				await state.update_data(group=group)
				break

		await state.set_state(SchedulesFrom.get_weekday)
		await call.message.edit_text("День недели:", reply_markup=weekday_inline_keyboard)

	@router.callback_query(SchedulesFrom.get_weekday, F.data.startswith("admin-weekday_"))
	async def get_weekday(self, call: CallbackQuery, state: FSMContext) -> None:
		await state.update_data(weekday=call.data.split("_")[1])

		data = await state.get_data()
		# schedule = await select_schedule(group_id=data['group'], weekday=int(data['weekday']))
		text_schedule = "Расписание пар на *день недели*:"
		await call.message.edit_text(text_schedule)
		# if schedule is None:
		#     await call.message.edit_text(text_schedule)

	@router.callback_query(SchedulesFrom.get_course, SchedulesFrom.get_group, SchedulesFrom.get_weekday,
								 F.data.startswith('back_'))
	async def process_back(self, call: CallbackQuery, state: FSMContext) -> None:
		data = call.data
		
		if data == "back_course":
			await state.clear()
			# user = await select_user(tg_id=call.from_user.id)

			if call.from_user.id in call.message.bot.config.tg_bot.admin_ids:
				await call.message.edit_text(f"<b>Админ-панель:</b> \n{description_admin_panel}",
											 reply_markup=admin_menu_inline)
			# elif user['role'] == 'moderator':
			#     await call.message.edit_text(f"<b>Админ-панель:</b> \n{description_admin_panel}",
			#                                  reply_markup=moderator_menu_inline)
		elif data == "back_group":
			await state.set_state(SchedulesFrom.get_course)
			await call.message.edit_text("Выберите курс:", reply_markup=choice_a_course_inline_keyboard)
		elif data == "back_weekday":
			course = (await state.get_data())["course"]
			await state.set_state(SchedulesFrom.get_group)
			await call.message.edit_text("Выберите группу:", reply_markup=group_inline_keyboard(course))
