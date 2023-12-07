from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton


# Кнопка принятия согласия на обработку данных (при регистрации)
select_confirm_regisrer = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Согласен",
            callback_data="confirm"
        )
    ]
])

