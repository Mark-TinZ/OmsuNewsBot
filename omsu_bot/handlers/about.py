from ctypes.wintypes import MSG
from email import message
import logging
import stat
from traceback import print_tb

from aiogram import Router
from aiogram.fsm.state import StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from omsu_bot import utils
import omsu_bot.data.language as lang
from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import RouterHandler
from omsu_bot.services.broadcaster import broadcast

logger = logging.getLogger(__name__)

class AboutForm(StatesGroup):
	about = HandlerState(
		text=lang.user_about,
		reply_markup=
			InlineKeyboardBuilder()
				.button(text="Предложить идею", callback_data="idea_ticket")
				.button(text="Сообщить о проблеме", callback_data="report_ticket")
				.as_markup()
	)
	
	about_idea_ticket = HandlerState(
		text=lang.user_about_idea,
		reply_markup=
			InlineKeyboardBuilder()
			.button(text="❌ Отмена", callback_data="cancel")
			.as_markup(),
		previous_state=about
	)

	about_report_ticket = HandlerState(
		text=lang.user_about_report,
		reply_markup=
			InlineKeyboardBuilder()
			.button(text="❌ Отмена", callback_data="cancel")
			.as_markup(),
		previous_state=about
	)
	


class About(RouterHandler):
	def __init__(self):
		super().__init__()
		
		router: Router = self.router

		@router.callback_query(AboutForm.about)
		async def start_ticket(call: CallbackQuery, state: FSMContext):
			data = call.data

			match data:
				case "idea_ticket":
					await AboutForm.about_idea_ticket.message_send(self.bot, state, call.message.chat)
				case "report_ticket":
					pass
				case _:
					await call.answer(text="В разработке...")
		
		@router.message(AboutForm.about_idea_ticket)
		async def about_idea_ticket(msg: Message, state: FSMContext):
			if await utils.throttling_assert(state): return
			
			text = msg.text
			if not text:
				text = msg.caption


			if not text or len(text) > 4000:
				return await msg.reply(lang.user_about_idea_error_len)
			
			rpl_msg = dict(
				text=(
					f"Тикет: <code>#id{msg.from_user.id}</code>\n"
					f"💡 <i>{text}</i>\n\n"
					f"Пользователь: @{msg.from_user.username}"
				),
				parse_mode="HTML"
			)

			await msg.reply(**rpl_msg)
			await broadcast(self.bot.tg, self.bot.config.bot.admin_ids, **rpl_msg)
			await state.clear()

		@router.message(AboutForm.about_report_ticket)
		async def about_report_ticket(msg: Message, state: FSMContext):
			if await utils.throttling_assert(state): return
			
			text = msg.text
			if not text:
				text = msg.caption


			if not text or len(text) > 4000:
				return await msg.reply(lang.user_about_idea_error_len)
			
			rpl_msg = dict(
				text=(
					f"Тикет: <code>#id{msg.from_user.id}</code>\n"
					f"🛠️ <i>{text}</i>\n\n"
					f"Пользователь: @{msg.from_user.username}"
				),
				parse_mode="HTML"
			)

			await msg.reply(**rpl_msg)
			await broadcast(self.bot.tg, self.bot.config.bot.admin_ids, **rpl_msg)
			await state.clear()

		@router.callback_query(AboutForm.about_idea_ticket, AboutForm.about_report_ticket)
		async def ticket_cancel(call: CallbackQuery, state: FSMContext):
			if await utils.throttling_assert(state): return
			
			data = call.data
			if data == "cancel":
				AboutForm.about.message_edit(self.bot, state, call.message, call.message.chat)
			else:
				await call.answer(text="В разработке...")