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


class HaduliForm(StatesGroup):
	haduli_eba = HandlerState(
		text="Дав-а-й е-ба-шш..."
	)


class Haduli(RouterHandler):
	def __init__(self):
		super().__init__()
		
		router: Router = self.router

		@router.message(Command("test"))
		async def handle_haduli(msg: Message, state: FSMContext) -> None:
			await HaduliForm.haduli_eba.message_send(self.bot, state, msg.chat, msg.message_id)

		@router.message(Command("putin"))
		async def handle_haduli(msg: Message, state: FSMContext) -> None:
			await msg.answer_video_note(FSInputFile("media/video/putin.mp4"))

		@router.message(HaduliForm.haduli_eba)
		async def shadow_fight(msg: Message, state: FSMContext) -> None:
			eba_list = parse_schedule_text(msg.text)
			res = "`{" + ", ".join(map(str, eba_list)) + "}`"
			await msg.answer(res, parse_mode="Markdown")

