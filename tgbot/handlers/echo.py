from aiogram import Router
from aiogram.types import Message

echo_router = Router()


@echo_router.message()
async def echo_msg(msg: Message):
    await msg.answer(msg.text)
