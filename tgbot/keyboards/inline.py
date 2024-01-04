from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.data.constants import list_group, callback_data_group

super_inline_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Супер!", callback_data="super")
        ]
    ]
)

agree_inline_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Согласен", callback_data="agree")
        ]
    ]
)

choice_a_role_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Студент", callback_data="student"),
            InlineKeyboardButton(text="Преподаватель", callback_data="teacher"),
        ]
    ]
)

course_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="1 курс", callback_data="course_1"),
            InlineKeyboardButton(text="2 курс", callback_data="course_2")
        ],
        [
            InlineKeyboardButton(text="3 курс", callback_data="course_3"),
            InlineKeyboardButton(text="4 курс", callback_data="course_4")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_course")
        ]
    ]
)


def group_inline_keyboard(course):
    groups = list_group[course]
    callbacks = callback_data_group[course]

    group_buttons = []
    all_buttons = []

    for key, val in enumerate(groups):
        group_buttons.append(InlineKeyboardButton(text=val, callback_data=callbacks[key]))
        if len(group_buttons) == 2 or key == len(groups) - 1:
            all_buttons.append(group_buttons)
            group_buttons = []

    all_buttons.append([InlineKeyboardButton(text="Назад", callback_data="back_group")])

    return InlineKeyboardMarkup(inline_keyboard=all_buttons)


yes_or_back_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да, все верно", callback_data="yes"),
            InlineKeyboardButton(text="Назад", callback_data="back_group")
        ]
    ]
)
