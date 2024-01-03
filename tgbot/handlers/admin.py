from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.data.constants import description_admin_panel
from tgbot.database.user import select_user
from tgbot.states.admin_states import SchedulesFrom
from tgbot.keyboards.inline_admin import admin_menu_inline, moderator_menu_inline, \
    choice_a_course_inline_keyboard, group_inline_keyboard, weekday_inline_keyboard

admin_router = Router()


@admin_router.message(F.text == "Админ-панель")
async def menu_admin(message: Message, state: FSMContext) -> None:
    state.clear()
    user = await select_user(tg_id=message.from_user.id)
    
    if message.from_user.id in message.bot.config.tg_bot.admin_ids:
        await message.answer(f"<b>Админ-панель:</b> \n{description_admin_panel}", reply_markup=admin_menu_inline)
    elif user['role'] == 'moderator':
        await message.answer(f"<b>Админ-панель:</b> \n{description_admin_panel}", reply_markup=moderator_menu_inline)


@admin_router.callback_query(F.data == "edit_schedules")
async def edit_schedule(call: CallbackQuery, state: FSMContext) -> None:
    if call.from_user.id in call.bot.config.tg_bot.admin_ids:
        await state.set_state(SchedulesFrom.get_course)
        await call.message.edit_text("Выберите курс:", reply_markup=choice_a_course_inline_keyboard)


@admin_router.callback_query(F.data.startswith("admin-course_"))
async def get_course(call: CallbackQuery, state: FSMContext) -> None:
    course = call.data.split("_")[1]
    await state.update_data(course=course)
    await state.set_state(SchedulesFrom.get_group)
    await call.message.edit_text("Выберите группу:", reply_markup=group_inline_keyboard(course))

@admin_router.callback_query(F.data.startswith("admin-group_"))
async def get_group(call: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(group=call.data.split("_")[1])
    await state.set_state(SchedulesFrom.get_weekday)
    await call.message.edit_text("День недели:", reply_markup=weekday_inline_keyboard)

@admin_router.callback_query(F.data.startswith('admin-back_'))
async def process_back(call: CallbackQuery, state: FSMContext) -> None:
    data = call.data

    if data == "admin-back_course":
        state.clear() 
        user = await select_user(tg_id=call.from_user.id)
        print(user)
        print(user["role"])

        if call.from_user.id in call.message.bot.config.tg_bot.admin_ids:
            await call.message.edit_text(f"<b>Админ-панель:</b> \n{description_admin_panel}", reply_markup=admin_menu_inline)
        elif user['role'] == 'moderator':
            await call.message.edit_text(f"<b>Админ-панель:</b> \n{description_admin_panel}", reply_markup=moderator_menu_inline)
    elif data == "admin-back_group":
        await state.set_state(SchedulesFrom.get_course)
        await call.message.edit_text("Выберите курс:", reply_markup=choice_a_course_inline_keyboard)
    elif data == "admin-back_weekday":
        data = await state.get_data()
        course = data["course"]
        await state.set_state(SchedulesFrom.get_group)
        await call.message.edit_text("Выберите группу:", reply_markup=group_inline_keyboard(course))