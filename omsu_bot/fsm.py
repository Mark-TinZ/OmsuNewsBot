
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message


class HandlerState(State):

	def __init__(self, name: str = None, content: str = None, message_call_handler = None):
		super().__init__()
		self.message_call_handler = message_call_handler
		self.content = content
		self.name = name

	async def message_call(self, message: Message, context: FSMContext, *args, **kwargs):
		await context.set_state(self)
		handler = self.message_call_handler
		if handler is None:
			if not self.content is None:
				await message.edit_text(self.content)
		else:
			await handler(message, context, *args, **kwargs)

	def handle_message_call(self, func):
		self.message_call_handler = func
		return func



