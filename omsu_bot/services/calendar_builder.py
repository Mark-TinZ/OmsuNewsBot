import calendar

from datetime import datetime, date
from omsu_bot.data.lang import phrase
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


def build(builder: InlineKeyboardBuilder, at: date):
	at_now = datetime.now()
	day_now = at_now.day
	month_now = at_now.month
	year_now = at_now.year

	day = at.day
	month = at.month
	month_name = phrase("ru/month_map").get(month, "{month_map}")
	year = at.year
	week_day, day_count = calendar.monthrange(year, month)

	for i in phrase("ru/weekday_map"):
		builder.button(text=i, callback_data="label")

	for i in range(week_day):
		builder.button(text=" ", callback_data="label")
	
	for i in range(1, day_count+1):
		if i == day_now and month == month_now and year == year_now:
			n = f"[{i}]"
		elif i == day:
			n = f">{i}<" #
		else:
			n = str(i)
		builder.button(text=n, callback_data=f"{i}")
	
	left = 7-day_count%7-week_day
	if left < 0:
		left = left+7
	elif left > 6:
		left = left-7
	
	for i in range(left):
		builder.button(text=" ", callback_data="label")
	
	builder.adjust(7)

	builder.row(
		InlineKeyboardButton(text="◀", callback_data="month_prev"),
		InlineKeyboardButton(text=f"{month_name}, {year}", callback_data="mlabel"),
		InlineKeyboardButton(text="▶", callback_data="month_next")
	)


def process(action: str, at: date):
	match action:
		case "month_prev":
			m = at.month-1
			y = at.year
			if m < 1:
				y -= 1
				m += 12
			return date(year=y, month=m, day=1)
		case "month_next":
			m = at.month+1
			y = at.year
			if m > 12:
				y += 1
				m -= 12
			return date(year=y, month=m, day=1)
		case _:
			if action.isdigit():
				return date(year=at.year, month=at.month, day=int(action))
	
