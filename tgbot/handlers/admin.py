from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from tgbot.keyboards.inline_admin import admin_menu_inline

admin_router = Router()


@admin_router.message(F.text == "Админ-панель")
async def menu_admin(message: Message) -> None:
    if message.from_user.id in message.bot.config.tg_bot.admin_ids:
        await message.answer("Админ-панель:", reply_markup=admin_menu_inline)


@admin_router.callback_query(F.data == "send_schedule")
async def send_schedule(call: CallbackQuery) -> None:
    pass
