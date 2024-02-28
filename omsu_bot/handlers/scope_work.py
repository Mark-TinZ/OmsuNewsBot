import logging
import re

from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, Chat, FSInputFile

from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from omsu_bot import utils

from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import RouterHandler
from aiogram.filters import Command

def parse_schedule_text(text: str) -> list:
	items: list = re.findall(r"(\d+-\d+|\d+|н/н|ч/н|н\\н|ч\\н)", text)
	if not items: return list()
	result: list = []
	flag = None
	
	for item in items:
		if "-" in item:
			start, end = map(int, item.split("-"))
			result.extend(range(start, end + 1))
		elif "н/н" in item or "н\\н" in item:
			flag = True
		elif "ч/н" in item or "ч\\н" in item:
			flag = False
		else:
			result.append(int(item))

	if flag:
		result = [x for x in result if x % 2 == 1]
	elif flag == False:
		result = [x for x in result if x % 2 == 0]
	return result


class ScopeWorkForm(StatesGroup):
	scope_work = HandlerState(
		text="Ладно, для начала просто напиши уч. недели)\nНе забудь нажать 'Отмена' после работы.",
		reply_markup=
			InlineKeyboardBuilder()
			.button(text="Отмена", callback_data="cancel")
			.as_markup()
	)


class ScopeWork(RouterHandler):
	def __init__(self):
		super().__init__()
		
		router: Router = self.router

		@router.message(Command("dana"))
		async def handle_haduli(msg: Message, state: FSMContext) -> None:
			await msg.answer_video_note(FSInputFile("media/video/dana.mp4"))

		@router.message(Command("scope_work"))
		async def handle_haduli(msg: Message, state: FSMContext) -> None:
			await ScopeWorkForm.scope_work.message_send(self.bot, state, msg.chat, msg.message_id)

		@router.message(ScopeWorkForm.scope_work)
		async def shadow_fight(msg: Message, state: FSMContext) -> None:
			eba_list = parse_schedule_text(msg.text)
			res = "`{" + ", ".join(map(str, eba_list)) + "}`"
			await msg.answer(res, parse_mode="Markdown")

		@router.callback_query(ScopeWorkForm.scope_work)
		async def cancel_work(call: CallbackQuery, state: FSMContext) -> None:
			await call.answer()
			await call.message.answer(text="Готово, задача закрыта.")
			await state.clear() 

