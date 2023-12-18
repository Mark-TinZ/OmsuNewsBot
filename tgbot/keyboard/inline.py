from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from tgbot.data.constants import group_message, callback_data_group

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

# TODO: Ужасный кстыль, нужно один раз запримать в таблицу при запуске и дать возможность обновлять таблицу командой.
def inline_keyboard_group(course: str | int) -> InlineKeyboardMarkup:
    if type(course) == int:
        course = f"course_{course}"

    groups: tuple = group_message[course]
    callbacks: tuple = callback_data_group[course]
    group_buttons: list = list()
    for key, val in enumerate(groups):
        group_buttons.append(InlineKeyboardButton(text=val, callback_data=callbacks[key]))

    buttons: list = [
        group_buttons,
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data="back_group"
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)