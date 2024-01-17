import math
import sqlalchemy as sa
import sqlalchemy.orm as sorm

from datetime import datetime, timedelta

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.utils.chat_action import ChatActionSender

from omsu_bot import utils
import omsu_bot.data.language as lang
from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import RouterHandler
from omsu_bot.database.models import Group, Subject, User, Student, Teacher, Lesson



def weeks_difference(start_date, end_date):
	days_difference = (end_date - start_date).days
	return (days_difference // 7) + 1



lesson_time = {
	1: "8:45-9:30 / 9:35-10:20",
	2: "10:30-11:15 / 11:20-12:05",
	3: "12:45-13:30 / 13:35-14:20",
	4: "14:30-15:15 / 15:20-16:05",
	5: "16:15-17:00 / 17:05-17:50",
	6: "18:00-18:45 / 18:50-19:35",
	7: "19:45-20:30 / 20:35-21:20",
	8: "21:30-22:15 / 22:20-23:05"
}


class ScheduleForm(StatesGroup):

	@staticmethod
	async def schedule_message(self, bot, context: FSMContext, for_datetime=False, tomorrow: bool = False):
		if not bot.db.is_online():
			await context.clear()
			return dict(
				text=lang.user_error_database_connection
			)
		await context.set_state(self)

		tg_id = context.key.user_id

		sess: sorm.Session = bot.db.session

		with sess.begin(): 
			user: User | None = sess.execute(sa.select(User).where(User.tg_id == tg_id)).scalar_one_or_none()

			if not user:
				return dict(
					text=lang.user_error_auth_unknown
				)

			## TIMING ##
			
			for_datetime = for_datetime or datetime.today()

			weekday = for_datetime.weekday()
			
			academic_start = bot.config.schedule.academic_start
			week_number = weeks_difference(academic_start, for_datetime.date())

			text = f"{for_datetime.strftime('%d.%m.%Y')}  -  "

			if user.role_id == "student":
				union = sess.execute(
					sa.select(Student, Group)
					.where(Student.user_id == user.id_)
					.join(Group, Group.id_ == Student.group_id)
				).first()

				if not (union and union[0] and union[1]):
					return dict(text=lang.user_error_database_logic)
				
				student, group = union

				lessons = sess.execute(
					sa.select(Lesson, Subject, Teacher)
					.where(Lesson.group_id == student.group_id, Lesson.weekday == weekday, Lesson.academic_weeks.contains((week_number,)))
					.order_by(Lesson.lesson_number)
					.join(Subject, Subject.id_ == Lesson.subject_id, isouter=True)
					.join(Teacher, Teacher.id_ == Lesson.teacher_id, isouter=True)
				)

				text += f"{group.name}\n\n"
				last_num = 0

				for lesson, subject, teacher in lessons:
					num = lesson.lesson_number
					if num - last_num > 1:
						text += "\n"
					last_num = num

					lesson_bounds = lesson_time.get(num, None)
					lesson_type_room = f"{lesson.type_lesson}. {lesson.room}"
					lesson_name = subject.name if subject else "Неизвестный"

					if len(lesson_name) + len(lesson_type_room) < 30:
						text += f"*{num}. {lesson_name}* ({lesson_type_room})\n"
					else:
						text += f"*{num}. {lesson_name}*\n - {lesson_type_room}\n"
					
					if lesson_bounds:
						text += f" - {lesson_bounds}\n"
					if teacher:
						text += f" - {teacher.name}\n"
				
				if last_num == 0:
					text += " 😄 Занятий нет..."

			elif user.role_id == "teacher":
				teacher: Teacher = sess.execute(sa.select(Teacher).where(Teacher.user_id == user.id_)).scalar_one_or_none()
				if not teacher:
					return dict(text=lang.user_error_database_logic)
				
				lessons = sess.execute(
					sa.select(Lesson, Subject, Group)
					.where(Lesson.teacher_id == teacher.id_, Lesson.weekday == weekday, Lesson.academic_weeks.contains((week_number,)))
					.order_by(Lesson.lesson_number)
					.join(Subject, Subject.id_ == Lesson.subject_id)
					.join(Group, Group.id_ == Lesson.group_id)
				)

				text += f"{teacher.name}\n\n"
				last_num = 0

				for lesson, subject, group in lessons:
					num = lesson.lesson_number
					if num - last_num > 1:
						text += "\n"
					last_num = num

					lesson_bounds = lesson_time.get(num, None)
					lesson_type_room = f"{lesson.type_lesson}. {lesson.room}"
					lesson_name = subject.name if subject else "Неизвестный"

					if len(lesson_name) + len(lesson_type_room) < 30:
						text += f"*{num}. {lesson_name}* ({lesson_type_room})\n"
					else:
						text += f"*{num}. {lesson_name}*\n - {lesson_type_room}\n"
					
					if lesson_bounds:
						text += f" - {lesson_bounds}\n"
					if group:
						text += f" - {group.name}\n"
				
				if last_num == 0:
					text += " 😄 Занятий нет..."
			
			return dict(
				text=text,
				reply_markup=None if tomorrow else self.reply_markup
			)
		
		
	schedule = HandlerState(
		message_handler=schedule_message,
		reply_markup=
			InlineKeyboardBuilder()
				.button(text="На завтра", callback_data="show_tomorrow")
				.as_markup()
	)


class Schedule(RouterHandler):
	def __init__(self):
		super().__init__()
		router: Router = self.router

		@router.callback_query(ScheduleForm.schedule)
		async def handle_schedule(call: CallbackQuery, state: FSMContext):
			if await utils.throttling_assert(state): return

			msg = call.message

			match call.data:
				case "show_tomorrow":
					await call.answer()
					await ScheduleForm.schedule.message_send(self.bot, state, msg.chat, for_datetime=datetime.today()+timedelta(days=1), tomorrow=True)
				case _:
					await call.answer(text="В разработке...")