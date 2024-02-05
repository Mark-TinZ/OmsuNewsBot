import json
import logging
import sqlalchemy as sa
import sqlalchemy.orm as sorm

from aiogram import Bot, Router
from datetime import datetime, timedelta
from aiogram.fsm.state import StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from omsu_bot import utils
import omsu_bot.data.language as lang
from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import RouterHandler
from omsu_bot.services import calendar_builder, broadcaster
from omsu_bot.database.models import Group, Subject, User, Student, Teacher, Lesson


def weeks_difference(start_date, end_date):
	days_difference = (end_date - start_date).days
	return (days_difference // 7) + 1


logger = logging.getLogger(__name__)
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




def rich_schedule(lessons, at: datetime | int, target: Teacher | Group = None):
	is_teacher = isinstance(target, Teacher)
	is_weekday = isinstance(at, int)
	text = f"{lang.weekday_map[at] if is_weekday else lang.weekday_map[at.weekday()]+', '+at.strftime('%d.%m.%Y')}  -  {target.name}\n\n"
	
	last_num = 0

	for lesson, subject, ext in lessons:
		num = lesson.lesson_number

		if is_teacher and last_num == num:
			if ext:
				text += f" - {ext.name}\n"
			last_num = num
			continue

		if num - last_num > 1:
			text += "\n"
		last_num = num

		lesson_bounds = lesson_time.get(num, None)
		lesson_type_room = f"{lesson.type_lesson} {lesson.room}"
		lesson_name = subject.name if subject else "Неизвестный"

		if len(lesson_name) + len(lesson_type_room) < 30:
			text += f"*{num}. {lesson_name}* ({lesson_type_room})\n"
		else:
			text += f"*{num}. {lesson_name}*\n - {lesson_type_room}\n"
		
		if lesson_bounds:
			text += f" - {lesson_bounds}\n"
		if ext:
			text += f" - {ext.name}\n"
	
	if last_num == 0:
		text += " 😄 Занятий нет..."
	
	return text


class ScheduleForm(StatesGroup):
	
	@staticmethod
	async def schedule_message(self, bot, context: FSMContext, at=None, show_calendar: bool = False):
		tg_id = context.key.user_id
		if not bot.db.is_online():
			await context.clear()
			return dict(
				text=lang.user_error_database_connection
			)
		await context.set_state(self)


		sess: sorm.Session = bot.db.session

		with sess.begin():
			user: User | None = sess.execute(sa.select(User).where(User.tg_id == tg_id)).scalar_one_or_none()

			if not user:
				logger.error(f"id={tg_id} не зарегистрированы!")
				return dict(
					text=lang.user_error_auth_unknown
				)
			
			at = at or datetime.today().date()

			weekday = at.weekday()
			academic_start = bot.config.schedule.academic_start
			week_number = weeks_difference(academic_start, at)

			target = None
			lessons = None

			if user.role_id == "student":
				union = sess.execute(
					sa.select(Student, Group)
					.where(Student.user_id == user.id_)
					.join(Group, Group.id_ == Student.group_id)
				).first()

				if not union: return dict(text=lang.user_error_database_logic)
				
				target = union[1]

				lessons = sess.execute(
					sa.select(Lesson, Subject, Teacher)
					.where(Lesson.group_id == target.id_, Lesson.weekday == weekday, Lesson.academic_weeks.contains((week_number,)))
					.order_by(Lesson.lesson_number)
					.join(Subject, Subject.id_ == Lesson.subject_id, isouter=True)
					.join(Teacher, Teacher.id_ == Lesson.teacher_id, isouter=True)
				).all()
			elif user.role_id == "teacher":
				target: Teacher = sess.execute(sa.select(Teacher).where(Teacher.user_id == user.id_)).scalar_one_or_none()
				
				if not target: return dict(text=lang.user_error_database_logic)

				lessons = sess.execute(
					sa.select(Lesson, Subject, Group) 
					.where(Lesson.teacher_id == target.id_, Lesson.weekday == weekday, Lesson.academic_weeks.contains((week_number,)))
					.order_by(Lesson.lesson_number)
					.join(Subject, Subject.id_ == Lesson.subject_id, isouter=True)
					.join(Group, Group.id_ == Lesson.group_id, isouter=True)
				).all()
		
			if not target:
				return dict(text=lang.user_error_database_logic)
			
			text = rich_schedule(lessons, at, target)

		
		await context.update_data(selected_date=at)

		builder = InlineKeyboardBuilder()
		if show_calendar:
			calendar_builder.build(builder, at)
		else:
			builder.button(text="На завтра", callback_data="show_tomorrow")
			builder.button(text="Календарь", callback_data="show_calendar")

			if tg_id in bot.config.bot.admin_ids:
				builder.button(text="Изменить", callback_data="edit_schedule")
			builder.adjust(2, 1)
		
		return dict(
			text=text,
			reply_markup=builder.as_markup()
		)

	schedule = HandlerState(message_handler=schedule_message)

	scope_selection = HandlerState()


class Schedule(RouterHandler):
	def __init__(self):
		super().__init__()
		router: Router = self.router

		@router.callback_query(ScheduleForm.schedule)
		async def handle_schedule(call: CallbackQuery, state: FSMContext):
			if await utils.throttling_assert(state, count=5): return

			await call.answer()
			msg = call.message

			if call.data == "mlabel":
				await msg.answer_video_note(FSInputFile("media/video/heli-maxwell.mp4"))


			data = await state.get_data()

			current_date = data.get("selected_date", None) or datetime.today().date()
			at = calendar_builder.process(call.data, current_date)

			if at:
				await ScheduleForm.schedule.message_edit(self.bot, 
					state, 
					msg, 
					at=at, 
					show_calendar=(call.data == "month_prev" or call.data == "month_next")
				)

			match call.data:
				case "show_tomorrow":
					await call.answer()
					await ScheduleForm.schedule.message_edit(
						self.bot, 
						state, 
						msg,
						at=current_date+timedelta(days=1)
					)
				case "show_calendar":
					await call.answer()

					builder = InlineKeyboardBuilder()
					calendar_builder.build(builder, current_date)

					await call.message.edit_reply_markup(reply_markup=builder.as_markup())
				case "edit_schedule":
					await call.answer()

					
				case _:
					await call.answer(text="В разработке...")
		
	@staticmethod
	async def schedule_scheduler(bot: Bot, db, config):
		sess: sorm.Session = db.session

		at = datetime.today().date()+timedelta(days=1)

		weekday = at.weekday()

		if weekday == 6:
			return

		academic_start = config.schedule.academic_start
		week_number = weeks_difference(academic_start, at)

		target = None
		lessons = None

		with sess.begin():
			users: sa.ScalarResult = sess.execute(sa.select(User)).scalars()

			for user in users:
				if not user:
					logger.error("An error occurred while trying to send a schedule.")
					continue

				settings_json = user.settings
				try:
					settings_dict = settings_json if isinstance(settings_json, dict) else json.loads(settings_json)
				except json.JSONDecodeError:
					settings_dict = dict()
				
				notifications_enabled = settings_dict.get("notifications_enabled", True)

				if not notifications_enabled:
					continue

				if user.role_id == "student":
					union = sess.execute(
						sa.select(Student, Group)
						.where(Student.user_id == user.id_)
						.join(Group, Group.id_ == Student.group_id)
					).first()

					if not union:
						logger.error("Logical exception, database entry is corrupted")
						continue
					
					target = union[1]

					lessons = sess.execute(
						sa.select(Lesson, Subject, Teacher)
						.where(Lesson.group_id == target.id_, Lesson.weekday == weekday, Lesson.academic_weeks.contains((week_number,)))
						.order_by(Lesson.lesson_number)
						.join(Subject, Subject.id_ == Lesson.subject_id, isouter=True)
						.join(Teacher, Teacher.id_ == Lesson.teacher_id, isouter=True)
					)
				elif user.role_id == "teacher":
					target: Teacher | None = sess.execute(sa.select(Teacher).where(Teacher.user_id == user.id_)).scalar_one_or_none()
					
					lessons = sess.execute(
						sa.select(Lesson, Subject, Group) 
						.where(Lesson.teacher_id == target.id_, Lesson.weekday == weekday, Lesson.academic_weeks.contains((week_number,)))
						.order_by(Lesson.lesson_number)
						.join(Subject, Subject.id_ == Lesson.subject_id, isouter=True)
						.join(Group, Group.id_ == Lesson.group_id, isouter=True)
					)
				
				if not target:
					logger.error("Logical exception, database entry is corrupted")
					continue

				text = "Ваше расписание на завтра:\n" + rich_schedule(lessons, at, target)
				mailing = broadcaster.Broadcast(bot, [user.tg_id])
				await mailing.send_message(text=text, parse_mode="Markdown")