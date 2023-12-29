from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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

choice_a_course_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="1 курс", callback_data="course_one"),
            InlineKeyboardButton(text="2 курс", callback_data="course_two")
        ],
        [
            InlineKeyboardButton(text="3 курс", callback_data="course_three"),
            InlineKeyboardButton(text="4 курс", callback_data="course_four")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_course")
        ]
    ]
)


def group_inline_keyboard(course: int):
    pass
