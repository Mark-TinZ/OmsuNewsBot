import logging
import sqlalchemy as sa
import sqlalchemy.orm as sorm

from aiogram import Router
from aiogram.fsm.state import StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.utils.chat_action import ChatActionSender

from omsu_bot import utils
from omsu_bot.data.lang import phrase
from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import RouterHandler
from omsu_bot.database.models import Group, User, Student, Teacher

logger = logging.getLogger(__name__)


class GroupsForm(StatesGroup):
	@staticmethod
	async def course_selection_message(self, bot, state: FSMContext, next_state: HandlerState = None, prev_state: HandlerState = None, title: str | None = None):
		await state.set_state(self)
		data = await state.get_data()
		if next_state:
			data["groups_next_state"] = next_state
		if prev_state:
			data["groups_prev_state"] = prev_state
		if title:
			data["groups_title"] = title
		await state.set_data(data)

		builder = (InlineKeyboardBuilder()
			.button(text=phrase("ru/groups/courses")[0], callback_data="1")
			.button(text=phrase("ru/groups/courses")[1], callback_data="2")
			.button(text=phrase("ru/groups/courses")[2], callback_data="3")
			.button(text=phrase("ru/groups/courses")[3], callback_data="4")
			.adjust(2)
		)

		if data["groups_prev_state"]:
			builder.row(InlineKeyboardButton(text=phrase("ru/return"), callback_data="return"))

		return dict(
			text=(f"{title}\n\n" if title else "") + self.text,
			reply_markup=builder.as_markup()
		)

	course_selection = HandlerState(
		text=phrase("ru/groups/selection_courses"),
		message_handler=course_selection_message
	)

	@staticmethod
	async def group_selection_message(self, bot, state: FSMContext):
		await state.set_state(self)
		if not bot.db.is_online():
			logger.error(f"id={state.key.user_id}, database is offline")
			return dict(
				text=phrase("ru/ext/err_db")
			)

		data = await state.get_data()
		course_number = data["groups_course_number"]
		title = data.get("groups_title", None)
		
		sess: sorm.Session = bot.db.session
		
		with sess.begin():
			res: sa.ScalarResult = sess.execute(sa.select(Group).where(Group.course_number == course_number, Group.is_enabled == True)).scalars()

		builder = InlineKeyboardBuilder()
		for group in res:
			builder.button(text=group.name, callback_data=f"{group.id_}/{group.name}")

		builder.adjust(2)
		builder.row(InlineKeyboardButton(text=phrase("ru/return"), callback_data="return"))

		return dict(
			text=(title+"\n" if title else "") + phrase("ru/groups/selection_group").format(course_number=course_number),
			reply_markup=builder.as_markup()
		)

	group_selection = HandlerState(message_handler=group_selection_message)


class Groups(RouterHandler):
	def __init__(self):
		super().__init__()
		
		router: Router = self.router

		@router.callback_query(GroupsForm.course_selection)
		async def handle_course_selection(call: CallbackQuery, state: FSMContext):
			if await utils.throttling_assert(state): return
			
			await call.answer()
			
			data = await state.get_data()
			prev_state = data.get("groups_prev_state", None)

			if call.data == "return" and prev_state:
				await prev_state.message_edit(self.bot, state, call.message)
				return
			
			async with ChatActionSender.typing(chat_id=call.message.chat.id, bot=self.bot.tg):
				if not call.data.isdigit():
					return
				
				course_number = int(call.data)
				await state.update_data(groups_course_number=course_number)
				await GroupsForm.group_selection.message_edit(self.bot, state, call.message)
		
		@router.callback_query(GroupsForm.group_selection)
		async def handle_group_selection(call: CallbackQuery, state: FSMContext):
			if await utils.throttling_assert(state): return
			
			await call.answer()
			
			if call.data == "return":
				await GroupsForm.course_selection.message_edit(self.bot, state, call.message)
				return
			
			c = call.data
			try:
				spl: int = c.find("/")
				group_id: int = int(c[:spl])
				group_name: str = c[(spl+1):]
			except:
				return
			
			await state.update_data(groups_group_id=group_id, groups_group_name=group_name)

			data = await state.get_data()
			next_state = data.get("groups_next_state", None)

			if next_state:
				await next_state.message_edit(self.bot, state, call.message)