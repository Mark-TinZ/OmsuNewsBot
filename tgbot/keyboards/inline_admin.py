from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

admin_menu_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Загрузить расписание", callback_data="send_schedule")
        ]
    ]
)
