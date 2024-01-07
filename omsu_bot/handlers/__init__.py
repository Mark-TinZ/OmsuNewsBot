from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from omsu_bot.handlers.admin import Administration

import aiogram
import omsu_bot
from omsu_bot.handlers.registration import Registration

handlers = [
    Registration,
    Administration
]

class Handler:
    bot: omsu_bot.OMSUBot | None = None

    async def enable(self, bot):
        self.bot = bot

    async def disable(self):
        self.bot = None

class RouterHandler(Handler):
    router: aiogram.Router = Router()

    async def enable(self, bot):
        await super().enable(bot)

        bot.dispatcher.include_router(self.router)

    @router.message(Command("test1"))
    async def handle_test1(self, msg: Message, fsm: FSMContext):
        await msg.answer("test1 response")


