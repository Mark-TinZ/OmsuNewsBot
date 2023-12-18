import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State

from tgbot.data import constants
from tgbot.keyboard.inline import select_confirm_regisrer, select_role, select_course, inline_keyboard_group

registration_router = Router()


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
        await msg.answer(constants.welcome_message)
        await asyncio.sleep(1)
        await state.set_state(StepsFormRegisterUser.Get_Confirm)
        await msg.answer(constants.confirm_message,
                         reply_markup=select_confirm_regisrer)
    else:
        pass


# Получение согласие и переход к след. этапу регистрации
@registration_router.callback_query(F.data == "confirm")
async def get_confirm(call: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(confirm=True)
    await call.message.answer(constants.register_message, reply_markup=select_role)
    await state.set_state(StepsFormRegisterUser.Get_role)


# Выбор роли *студент*
@registration_router.callback_query(F.data == "student")
async def get_student(call: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(role="student")
    await call.message.answer("Выберите курс:", reply_markup=select_course)
    await state.set_state(StepsFormRegisterUser.Get_Course)

# Выбор роли *препадователь*
@registration_router.callback_query(F.data == "teacher")
async def get_teacher(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.answer("nope")


# Выбор курса (студент)
@registration_router.callback_query(F.data.split("_")[0] == "course")
async def get_course(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.answer(f"Выберите группу:", reply_markup=inline_keyboard_group(call.data))


@registration_router.callback_query(F.data == "back_course")
async def back_register(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(StepsFormRegisterUser.Get_Confirm)
    await get_confirm(call, state)


@registration_router.callback_query(F.data == "back_group")
async def back_role(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(StepsFormRegisterUser.Get_role)
    await get_student(call, state)