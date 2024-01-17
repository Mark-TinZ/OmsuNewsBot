
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from datetime import datetime, timedelta, date
import omsu_bot.data.language as lang
import calendar


def build(builder: InlineKeyboardBuilder, at: date):
	month = at.month
	month_name = lang.month_map[month]
	year = at.year
	week_day, day_count = calendar.monthrange(year, month)

	
	for i in range(1, day_count+1):
		n = str(i)
		builder.button(text=n, callback_data=n)
	
	builder.adjust(7)

	builder.row(
		InlineKeyboardButton(text="<", callback_data="month_prev"),
		InlineKeyboardButton(text=f"{month_name}, {year}", callback_data="month_label"),
		InlineKeyboardButton(text=">", callback_data="month_next")
	)

