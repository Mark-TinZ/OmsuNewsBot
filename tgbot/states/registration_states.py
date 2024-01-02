from aiogram.fsm.state import StatesGroup, State

class RegisterFrom(StatesGroup):
    get_msg = State()
    get_super = State()
    get_agree = State()
    get_role = State()
    get_course = State()
    get_group = State()