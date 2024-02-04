import re
import logging

from aiogram import F, Router
from aiogram.fsm.state import StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder

from omsu_bot import utils
import omsu_bot.data.language as lang
from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import RouterHandler
from omsu_bot.services.broadcaster import Broadcast

logger = logging.getLogger(__name__)

def parse_answer_data(text: str):
	pattern = r"#id(\d+)"
	ids = re.findall(pattern, text)
	remaining_text = re.sub(pattern, '', text)
	return map(int, ids), remaining_text.strip()



class AboutForm(StatesGroup):
	about = HandlerState(
		text=lang.user_about,
		reply_markup=
			InlineKeyboardBuilder()
				.button(text="Предложить идею/Сообщить о проблеме", callback_data="idea_ticket")
				# .button(text="Сообщить о проблеме", callback_data="report_ticket")
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
			
			mailing = Broadcast(self.bot.tg, self.bot.config.bot.admin_ids)
			await mailing.send_message(
				text=(
					f"Тикет: <code>#id{msg.from_user.id}</code>\n"
					f"💡 {text}\n\n"
					f"Пользователь: @{msg.from_user.username}"
				),
				parse_mode="HTML"
			)
			await msg.reply(lang.user_about_idea_answer)
			await state.clear() 


		@router.callback_query(AboutForm.about_idea_ticket)
		async def about_idea_ticket_call(call: CallbackQuery, state: FSMContext):
			data = call.data 
			if data == "cancel":
				await AboutForm.about.message_edit(self.bot, state, call.message, call.message.chat)
			else:
				await call.answer(text="В разработке...")

		@router.message(Command(commands="answer"))
		async def answer_ticket(msg: Message, command: CommandObject):
			if msg.from_user.id not in self.bot.config.bot.admin_ids: return
			args = command.args
			if args:
				ids, text = parse_answer_data(args)
				if ids and text:
					send_message = f"💼 <b>Ответ от Администратора</b>\n\n{text}"
					mailing = Broadcast(self.bot.tg, ids)
					await mailing.send_message(text=send_message, parse_mode="HTML")
					await msg.reply("Ваш ответ успешно был отправлен пользователю!")
		


		@router.message(F.reply_to_message & F.reply_to_message.text & F.reply_to_message.text.regexp(r"^Тикет: #id(\d+)\n").as_("ticket_author_id"))
		async def answer_ticket_message(msg: Message, ticket_author_id: re.Match):
			if msg.from_user.id not in self.bot.config.bot.admin_ids: return

			ticket_author_id = ticket_author_id.group(1)
			if not (ticket_author_id and ticket_author_id.isdigit()): return
			ticket_author_id = int(ticket_author_id)

			text = msg.text

			if text:
				send_message = f"💼 <b>Ответ от Администратора</b>\n\n{text}"
				mailing = Broadcast(self.bot.tg, [ticket_author_id])
				await mailing.send_message(text=send_message, parse_mode="HTML")
				await msg.reply("Ваш ответ успешно был отправлен пользователю!")
