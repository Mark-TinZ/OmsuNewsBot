from ast import arg
import pandas
import logging
import sqlalchemy as sa
import sqlalchemy.orm as sorm

from aiogram import Router
from aiogram.fsm.state import StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject

from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import RouterHandler

logger = logging.getLogger(__name__)


class ExelModelForm(StatesGroup):
	pass

class ExelModel(RouterHandler):
	def __init__(self):
		super().__init__()
		
		router: Router = self.router

		@router.message(Command(commands="get_exel"))
		async def get_exel(msg: Message, command: CommandObject):
			args = command.args

		@router.message(Command(commands="load_exel"))
		async def looad_exel(msg: Message, command: CommandObject):
			args = command.args