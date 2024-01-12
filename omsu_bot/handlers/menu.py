from mailbox import Message
import sqlalchemy as sa
import sqlalchemy.orm as sorm

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup

import omsu_bot.data.language as lang
from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import RouterHandler


class MenuForm(StatesGroup):
	pass


class Menu(RouterHandler):
	def __init__(self):
		super().__init__()
		
		router: Router = self.router

	@Router.message(F.text == "Расписание")
	async def hendle_schedule(msg: Message):
		pass
