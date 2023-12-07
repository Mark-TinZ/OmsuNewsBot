from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

start_router = Router()


class StepsFormRegisterUser(StatesGroup):
    Get_Confirm = State()
    Get_role = State()
    Get_Course = State()
    Get_Group = State()


async def start_registr(msg: Message, state: FSMContext):
    await msg.answer("Для функционирования бот собирает и хранит информацию о вашей группе, курсе и идентификатор вашего телеграмма студента в зашифрованном виде. Пожалуйста, подтвердите свое согласие, так как без этой информации бот не сможет предоставить полноценный функционал.",
        reply_markup=)
    await 

async def get_confirm(call: )
