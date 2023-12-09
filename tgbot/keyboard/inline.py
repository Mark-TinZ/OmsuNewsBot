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

# Кнопки выбора роли
select_role = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="Студент",
            callback_data="student"
        ),
        InlineKeyboardButton(
            text="Преподаватель",
            callback_data="teacher"
        )
    ]
])

# Кнопки выбора курса
select_course = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text="1 курс",
            callback_data="course_1"
        ),
        InlineKeyboardButton(
            text="2 курс",
            callback_data="course_2"
        ),
        InlineKeyboardButton(
            text="3 курс",
            callback_data="course_3"
        ),
        InlineKeyboardButton(
            text="4 курс",
            callback_data="course_4"
        )
    ],
    [
        InlineKeyboardButton(
            text="Назад",
            callback_data="back_course"
        )
    ]
])
