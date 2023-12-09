import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State

from tgbot.data.constants import welcome_message, agreement_message
from tgbot.keyboard.inline import select_confirm_regisrer, select_role, select_course

registration_router = Router()


# TODO: переместить этот класс в необходимое место.
# Машина состояний регистрации пользователя
class StepsFormRegisterUser(StatesGroup):
    Get_Confirm = State()
    Get_role = State()
    Get_Course = State()
    Get_Group = State()


# Команда: /start
@registration_router.message(CommandStart())
async def start(msg: Message, state: FSMContext) -> None:
    # Проверка зарегистрирован пользователь? Если нет, то выводим сообщение.
    if not False:
        await msg.answer(welcome_message)
        await asyncio.sleep(1)
        await msg.answer(agreement_message,
                         reply_markup=select_confirm_regisrer)
        await state.set_state(StepsFormRegisterUser.Get_Confirm)
    else:
        pass


# TODO: Тут нужно разобраться, завтра займусь этим
# Получение согласие и переход к след. этапу регистрации
@registration_router.callback_query(F.data == "confirm")
async def get_confirm(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.answer("""Для начала вам нужно
зарегистрироваться.

Выберите роль:""", reply_markup=select_role)
    await state.set_data(confirm=True)
    await state.get_state(StepsFormRegisterUser.Get_role)


# выбор роли студент
@registration_router.callback_query(F.data == "student")
async def get_student(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.answer("Выберите курс:", reply_markup=select_course)



@registration_router.callback_query(F.data.split("_")[0] == "course")
async def get_course(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.answer(f"Выберите группу: {call.data}")


@registration_router.callback_query(F.data == "back_course")
async def get_course(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.answer(f"Выберите группу: {call.data}")
