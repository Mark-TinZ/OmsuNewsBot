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

# Кнопка выбора роли
select_role = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Студент",
            callback_data="student"
        ),
        InlineKeyboardButton(
            text="Преподователь",
            callback_data="teacher"
        )
    ]
])

