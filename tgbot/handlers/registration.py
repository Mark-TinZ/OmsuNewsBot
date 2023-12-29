from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.data.constants import greeting_message, user_agreement_message
from tgbot.database.user import select_user
from tgbot.keyboards.inline import super_inline_button, agree_inline_button, choice_a_role_inline_keyboard, \
    choice_a_course_inline_keyboard, group_inline_keyboard

registration_router = Router()


@registration_router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await state.clear()

    user = await select_user(tg_id=message.from_user.id)  # экземпляр в виде tuple либо None

    if user is None:
        await message.answer(greeting_message, reply_markup=super_inline_button)
    else:
        await message.answer("Чем могу помочь?")


@registration_router.callback_query(F.data == "super")
async def user_agreement(call: CallbackQuery):
    await call.message.edit_text(user_agreement_message, reply_markup=agree_inline_button)


@registration_router.callback_query(F.data == "agree")
async def choice_a_role(call: CallbackQuery):
    await call.message.edit_text("Для начала вам нужно зарегистрироваться.\n\nВыберите роль:",
                                 reply_markup=choice_a_role_inline_keyboard)


@registration_router.callback_query(F.data.in_({"student", "teacher"}))
async def choice_a_course(call: CallbackQuery):
    select_role = call.data

    if select_role == "student":
        await call.message.edit_text("Выберите курс:", reply_markup=choice_a_course_inline_keyboard)
    elif select_role == "teacher":
        await call.message.answer("В разработке...")
        await call.answer()


@registration_router.callback_query(F.data.startswith("course_"))
async def choice_a_group(call: CallbackQuery):
    await call.message.edit_text("Выберите группу:",
                                 group_inline_keyboard(int(call.data.split("_")[1])))


@registration_router.callback_query(F.data.startswith('back_'))
async def process_back(call: CallbackQuery):
    data = call.data

    if data == "back_course":
        await call.message.edit_text("Для начала вам нужно зарегистрироваться.\n\nВыберите роль:",
                                     reply_markup=choice_a_role_inline_keyboard)

    await call.answer()
