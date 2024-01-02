from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from aiogram.types import Message, CallbackQuery

from tgbot.states.registration_states import RegisterFrom
from tgbot.data.constants import greeting_message, user_agreement_message, callback_data_group, list_group
from tgbot.database.user import select_user, add_user
from tgbot.keyboards.inline import super_inline_button, agree_inline_button, choice_a_role_inline_keyboard, \
    choice_a_course_inline_keyboard, group_inline_keyboard, yes_or_back_inline_keyboard
from tgbot.keyboards.reply import menu_keyboard
registration_router = Router()

@registration_router.message(F.text == "/start")
async def start(message: Message, state: FSMContext) -> None:
    get_state = await state.get_state()
    if get_state is not None:
        data = await state.get_data()
        msg = data.get("get_msg")
        await message.bot.delete_message(message.chat.id, msg)
        await state.clear()
    user = await select_user(tg_id=message.from_user.id)  # экземпляр в виде tuple либо None

    if user is None:
        await state.set_state(RegisterFrom.get_msg)
        msg = await message.answer(greeting_message, reply_markup=super_inline_button)
        await state.update_data(get_msg=msg.message_id)
        await state.set_state(RegisterFrom.get_super)
    else:
        await message.answer("Чем могу помочь?", reply_markup=menu_keyboard(call.from_user.id))


@registration_router.callback_query(F.data == "super")
async def user_agreement(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(RegisterFrom.get_agree)
    await call.message.edit_text(user_agreement_message, reply_markup=agree_inline_button)

@registration_router.callback_query(F.data == "agree")
async def choice_a_role(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(RegisterFrom.get_role)
    await call.message.edit_text("Для начала вам нужно зарегистрироваться.\n\nВыберите роль:",
                                 reply_markup=choice_a_role_inline_keyboard)


@registration_router.callback_query(F.data.in_({"student", "teacher"}))
async def choice_a_course(call: CallbackQuery, state: FSMContext) -> None:
    select_role = call.data

    if select_role == "student":
        await state.update_data(role=select_role)
        await state.set_state(RegisterFrom.get_course)
        await call.message.edit_text("Выберите курс:", reply_markup=choice_a_course_inline_keyboard)
    elif select_role == "teacher":
        await call.message.answer("В разработке...")
        await call.answer()


@registration_router.callback_query(F.data.startswith("course_"))
async def choice_a_group(call: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(course=call.data.split("_")[1])
    await state.set_state(RegisterFrom.get_group)
    await call.message.edit_text("Выберите группу:", reply_markup=group_inline_keyboard(call.data.split("_")[1]))


@registration_router.callback_query(F.data.startswith("group_"))
async def yes_or_back(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await call.answer(data["course"])
    course = data["course"]

    for key, val in enumerate(callback_data_group[course]):
        if val.startswith(call.data):
            group = list_group[course][key]
            await state.update_data({"group": group})
            break

    await call.message.edit_text(f"Курс: {course}\nГруппа: {group}\n\nВсе верно?",
                                 reply_markup=yes_or_back_inline_keyboard)


@registration_router.callback_query(F.data == "yes")
async def adding_a_user_to_the_database(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.delete()

    data = await state.get_data()
    role = data["role"]
    course = data["course"]
    group = data["group"]

    await add_user(call.from_user.id, role, int(course), group)

    await call.message.answer("Отлично! Вы успешно зарегистрированы. Приятного пользования!",
                              reply_markup=menu_keyboard(call.from_user.id))


@registration_router.callback_query(F.data.startswith('back_'))
async def process_back(call: CallbackQuery) -> None:
    data = call.data

    if data == "back_course":
        await call.message.edit_text("Для начала вам нужно зарегистрироваться.\n\nВыберите роль:",
                                     reply_markup=choice_a_role_inline_keyboard)
    elif data == "back_group":
        await call.message.edit_text("Выберите курс:", reply_markup=choice_a_course_inline_keyboard)