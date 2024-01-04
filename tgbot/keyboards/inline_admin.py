from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.data.constants import list_group, callback_data_group

admin_menu_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Расписание", callback_data="edit_schedules")
        ],
        [
            InlineKeyboardButton(text="Пользователи", callback_data="edit_users")
        ]
        ,
        [
            InlineKeyboardButton(text="Написать новость", callback_data="send_news")
        ]
    ]
)

moderator_menu_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Расписание", callback_data="edit_schedules")
        ],
    ]
)

choice_a_course_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="1 курс", callback_data="admin-course_1"),
            InlineKeyboardButton(text="2 курс", callback_data="admin-course_2")
        ],
        [
            InlineKeyboardButton(text="3 курс", callback_data="admin-course_3"),
            InlineKeyboardButton(text="4 курс", callback_data="admin-course_4")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="admin-back_course")
        ]
    ]
)


def group_inline_keyboard(course: str) -> InlineKeyboardMarkup:
    groups = list_group[course]
    callbacks = callback_data_group[course]

    group_buttons = []
    all_buttons = []

    for key, val in enumerate(groups):
        group_buttons.append(InlineKeyboardButton(text=val, callback_data="admin-" + callbacks[key]))
        if len(group_buttons) == 2 or key == len(groups) - 1:
            all_buttons.append(group_buttons)
            group_buttons = []

    all_buttons.append([InlineKeyboardButton(text="Назад", callback_data="admin-back_group")])

    return InlineKeyboardMarkup(inline_keyboard=all_buttons)


weekday_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Пн", callback_data="weekday_1"),
            InlineKeyboardButton(text="Вт", callback_data="weekday_2"),
            InlineKeyboardButton(text="Ср", callback_data="weekday_3")
        ],
        [
            InlineKeyboardButton(text="Чт", callback_data="weekday_4"),
            InlineKeyboardButton(text="Пт", callback_data="weekday_5"),
            InlineKeyboardButton(text="Сб", callback_data="weekday_6"),
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_weekday")
        ]
    ]
)
