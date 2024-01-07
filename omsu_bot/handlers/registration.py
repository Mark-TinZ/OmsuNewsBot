from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from omsu_bot.data.constants import greeting_message, user_agreement_message, callback_data_group, list_group
from omsu_bot.handlers import RouterHandler
from omsu_bot.keyboards.inline_user import super_inline_button, agree_inline_button, choice_a_role_inline_keyboard, \
    choice_a_course_inline_keyboard, group_inline_keyboard, yes_or_back_inline_keyboard
from omsu_bot.keyboards.reply import menu_keyboard
from omsu_bot.states.registration_states import RegisterFrom


class Registration(RouterHandler):
    router: Router = super().router

    @router.message(F.text == "/start")
    async def start(self, message: Message, state: FSMContext) -> None:
        get_state = await state.get_state()

        if get_state is not None:
            data = await state.get_data()
            msg = data.get("get_msg")
            if msg is not None:
                await message.bot.delete_message(message.chat.id, msg.message_id)
            await state.clear()

        # user = await select_user(tg_id=message.from_user.id)
        # if user is None:
        if True:
            msg = await message.answer(greeting_message, reply_markup=super_inline_button)
            await state.update_data(get_msg=msg)
            await state.set_state(RegisterFrom.get_super)
        else:
            await message.answer("Чем могу помочь?", reply_markup=menu_keyboard(message.from_user.id))

    @router.callback_query(RegisterFrom.get_super, F.data == "super")
    async def user_agreement(self, call: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(RegisterFrom.get_agree)
        await call.message.edit_text(user_agreement_message, reply_markup=agree_inline_button)

    @router.callback_query(RegisterFrom.get_agree, F.data == "agree")
    async def choice_a_role(self, call: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(RegisterFrom.get_role)
        await call.message.edit_text("Для начала вам нужно зарегистрироваться.\n\nВыберите роль:",
                                     reply_markup=choice_a_role_inline_keyboard)

    @router.callback_query(RegisterFrom.get_role, F.data.in_({"student", "teacher"}))
    async def choice_a_course(self, call: CallbackQuery, state: FSMContext) -> None:
        select_role = call.data

        if select_role == "student":
            await state.update_data(role=select_role)
            await state.set_state(RegisterFrom.get_course)
            await call.message.edit_text("Выберите курс:", reply_markup=choice_a_course_inline_keyboard)
        elif select_role == "teacher":
            await call.message.answer("В разработке...")
            await call.answer()

    @router.callback_query(RegisterFrom.get_course, F.data.startswith("course_"))
    async def choice_a_group(self, call: CallbackQuery, state: FSMContext) -> None:
        course = call.data.split("_")[1]
        await state.update_data(course=course)
        await state.set_state(RegisterFrom.get_group)
        await call.message.edit_text("Выберите группу:", reply_markup=group_inline_keyboard(course))

    @router.callback_query(RegisterFrom.get_group, F.data.startswith("group_"))
    async def yes_or_back(self, call: CallbackQuery, state: FSMContext) -> None:
        data = await state.get_data()
        course = data["course"]

        for key, val in enumerate(callback_data_group[course]):
            if val.startswith(call.data):
                group = list_group[course][key]
                await state.update_data(group=group)
                break

        await call.message.edit_text(f"Курс: {course}\nГруппа: {group}\n\nВсе верно?",
                                     reply_markup=yes_or_back_inline_keyboard)

    @router.callback_query(F.data == "yes")
    async def adding_a_user_to_the_database(self, call: CallbackQuery, state: FSMContext) -> None:
        await call.message.delete()

        data = await state.get_data()
        role = data["role"]
        course = data["course"]
        group = data["group"]

        await state.clear()
        # await add_user(call.from_user.id, role, int(course), group)
        await call.message.answer("Отлично! Вы успешно зарегистрированы. Приятного пользования!",
                                  reply_markup=menu_keyboard(call.from_user.id))

    @router.callback_query(RegisterFrom.get_course, RegisterFrom.get_group, F.data.startswith('back_'))
    async def process_back(self, call: CallbackQuery, state: FSMContext) -> None:
        data = call.data

        if data == "back_course":
            await state.set_state(RegisterFrom.get_role)
            await call.message.edit_text("Для начала вам нужно зарегистрироваться.\n\nВыберите роль:",
                                         reply_markup=choice_a_role_inline_keyboard)
        elif data == "back_group":
            await state.set_state(RegisterFrom.get_course)
            await call.message.edit_text("Выберите курс:", reply_markup=choice_a_course_inline_keyboard)
