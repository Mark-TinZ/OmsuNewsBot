import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State

from tgbot.keyboard.InlineKeyboard import select_confirm_regisrer, select_role

start_router = Router()


# TODO: переместить этот класс в необходимое место.
# Машина состояний регистрации пользователя
class StepsFormRegisterUser(StatesGroup):
    Get_Confirm = State()
    Get_role = State()
    Get_Course = State()
    Get_Group = State()

# Команда: /start
@start_router.message(CommandStart())
async def start(msg: Message, state: FSMContext) -> None:
    # Проверка зарегистрирован пользователь? Если нет то выводим сообщение.
    if not False:
        await msg.answer(f"""Приветствую тебя, <b>{msg.from_user.full_name}</b>! 😊

Я - твой персональный бот, созданный для того, чтобы помочь тебе следить за расписанием учебных занятий. Теперь ты сможешь легко получать информацию о парах в любое время!

Кроме того, я умею считать недели. Это очень удобно, если тебе нужно знать, какая неделя учебная, или сколько недель осталось до конца семестра.

Просто введи команду /help, чтобы узнать, как со мной работать. Я готов помочь тебе в любое время! 🤖""")
        await asyncio.sleep(1)
        await msg.answer(
            "Для функционирования бот собирает и хранит информацию о вашей группе, курсе и идентификатор вашего телеграмма студента в зашифрованном виде. Пожалуйста, подтвердите свое согласие, так как без этой информации бот не сможет предоставить полноценный функционал.",
            reply_markup=select_confirm_regisrer)
        await state.set_state(StepsFormRegisterUser.Get_Confirm)


# Получение согласие и переход к след. этапу регистрации
@start_router.callback_query(F.data == "confirm")
async def get_confirm(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.answer("""Для начала вам нужно
зарегистрироваться.

Выберите роль:""", reply_markup=select_role)

# Ф-ция студента
@start_router.callback_query(F.data == "student")
async def get_student(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.answer("Выберите курс:")