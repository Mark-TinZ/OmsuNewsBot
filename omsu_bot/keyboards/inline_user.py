from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

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

def group_inline_keyboard(groups: list) -> InlineKeyboardMarkup:
	builder = InlineKeyboardBuilder()

	for key in groups:
		builder.button(text=key[0], callback_data="group_"+str(key[1])+"_"+key[0])	
		builder.adjust(2)
	builder.button(text="Назад", callback_data="back_group")

	return builder.as_markup()

yes_or_back_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да, все верно", callback_data="yes"),
            InlineKeyboardButton(text="Назад", callback_data="back_group")
        ]
    ]
)