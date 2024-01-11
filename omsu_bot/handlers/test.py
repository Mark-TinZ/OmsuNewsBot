from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, Chat

from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import RouterHandler
from aiogram.filters import Command


class TestForm(StatesGroup):
	request_approval = HandlerState(
		text="Вы *готовы*?",
		reply_markup=
			InlineKeyboardBuilder()
				.button(text="Да, давайте", callback_data="approve")
				.button(text="Нет, отмена", callback_data="cancel")
				.as_markup()
	)


	@staticmethod
	async def request_hello_edit(bot, context: FSMContext, msg: Message, chat: Chat):
		await context.update_data(message_id=msg.message_id)
		await msg.edit_text("Скажи **привет**")

	request_hello = HandlerState(message_edit_handler=request_hello_edit)


	@staticmethod
	async def request_number_message(bot, context: FSMContext):
		return dict(
			text="Выберите число",
			reply_markup=
				InlineKeyboardBuilder()
					.button(text="1", callback_data="1")
					.button(text="2", callback_data="2")
					.button(text="3", callback_data="3")
					.button(text="4", callback_data="4")
					.adjust(1, 2, 1)
					.as_markup()
		)

	request_number = HandlerState(message_handler=request_number_message)





class Test(RouterHandler):
	def __init__(self):
		super().__init__()
		
		router: Router = self.router

		@router.message(Command("test"))
		async def handle_test(msg: Message, state: FSMContext) -> None:
			await TestForm.request_approval.message_send(self.bot, state, msg.chat, msg.message_id)

		@router.callback_query(TestForm.request_approval)
		async def request_approval_response(call: CallbackQuery, state: FSMContext) -> None:
			if call.data == "approve":
				await TestForm.request_hello.message_edit(self.bot, state, call.message)
			else:
				await state.clear()
				await state.set_state()
				await call.message.edit_text(text="Операция отменена...")

		@router.message(TestForm.request_hello)
		async def request_hello_response(msg: Message, state: FSMContext) -> None:
			data = await state.get_data()
			message_id = data.get("message_id", None)
			if message_id and msg.text.lower() == "привет":
				del data["message_id"]
				await state.update_data(data=data)
				await TestForm.request_number.message_edit(self.bot, state, message_id, msg.chat)

		@router.callback_query(TestForm.request_number)
		async def request_number_response(call: CallbackQuery, state: FSMContext) -> None:
			await call.message.edit_text("Загаданное число: "+call.data)
			await state.clear()
			await state.set_state()


