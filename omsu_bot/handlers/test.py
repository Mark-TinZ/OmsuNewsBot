from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from omsu_bot.fsm import HandlerState
from omsu_bot.handlers import RouterHandler
from aiogram.filters import Command


class TestForm(StatesGroup):
	request_approval = State()

	@staticmethod
	async def request_hello_call(msg: Message, context: FSMContext):
		await context.update_data(message=msg.message_id)
		await msg.edit_text("Скажи **привет**")

	request_hello = HandlerState(message_call_handler=request_hello_call)


	@staticmethod
	async def request_number_call(msg: Message, context: FSMContext):


		await msg.edit_text(
			"Выберите число",
			reply_markup=
				(InlineKeyboardBuilder()
					.button(text="1", callback_data="1")
					.button(text="2", callback_data="2")
					.button(text="3", callback_data="3")
					.button(text="4", callback_data="4")
				).as_markup()
		)

	request_number = HandlerState(message_call_handler=request_number_call)





class Test(RouterHandler):
	def __init__(self):
		router: Router = self.router

		@router.message(Command("test"))
		async def handle_test(msg: Message, state: FSMContext) -> None:
			await state.set_state(TestForm.request_approval)
			await msg.answer(
				"Вы готовы?",
				reply_markup=
					(InlineKeyboardBuilder()
					 .button(text="Да, готовы", callback_data="approve")
					 ).as_markup()
			)

		@router.callback_query(TestForm.request_approval)
		async def request_approval_response(call: CallbackQuery, state: FSMContext) -> None:
			if call.data == "approve":
				await TestForm.request_hello.message_call(call.message, state)

		@router.message(TestForm.request_hello)
		async def request_hello_response(msg: Message, state: FSMContext) -> None:
			reply_to = msg.reply_to_message
			data = await state.get_data()
			if isinstance(reply_to, Message) and reply_to.message_id == data.get("message", None) and msg.text.lower() == "привет":
				del data["message"]
				await state.update_data(data=data)
				await TestForm.request_number.message_call(reply_to, state)

		@router.callback_query(TestForm.request_number)
		async def request_number_response(call: CallbackQuery, state: FSMContext) -> None:
			await call.message.edit_text("Загаданное число: "+call.data)
			await state.clear()
			await state.set_state()


