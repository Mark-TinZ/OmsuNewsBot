from aiogram.fsm.state import StatesGroup, State


class SchedulesFrom(StatesGroup):
    get_course = State()
    get_group = State()
    get_weekday = State()
    get_pairs = State()
