from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from omsu_bot.config import load_config


# 
def menu_keyboard(tg_id: int) -> ReplyKeyboardMarkup:
	admins = load_config().tg_bot.admin_ids
	if tg_id not in admins:
		keyboard = ReplyKeyboardMarkup(
			keyboard=[
				[
					KeyboardButton(text="Расписание"),
					KeyboardButton(text="Настройки")
				],
				[
					KeyboardButton(text="О боте")
				]
			],
			resize_keyboard=True
		)
	else:
		keyboard = ReplyKeyboardMarkup(
			keyboard=[
				[
					KeyboardButton(text="Расписание"),
					KeyboardButton(text="Настройки")
				],
				[
					KeyboardButton(text="О боте"),
					KeyboardButton(text="Админ-панель")
				]
			],
			resize_keyboard=True
		)

	return keyboard
