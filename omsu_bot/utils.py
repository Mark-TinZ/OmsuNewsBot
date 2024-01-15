import aiogram
from aiogram.fsm.context import FSMContext


async def remove_context(state: FSMContext, tg: aiogram.Bot):
	data = await state.get_data()

	msg_id = data.get("state_context_message_id", None)

	if msg_id:
		del data["state_context_message_id"]
		update = state.set_data(data)

		chat_id = state.key.chat_id

		await tg.edit_message_reply_markup(
			chat_id=chat_id,
			message_id=msg_id
		)
		await update


async def register_context(state: FSMContext, message: aiogram.types.Message | int, safe: bool = False):
	if not safe:
		await remove_context(state, message.bot)

	msg_id = message if isinstance(message, int) else message.message_id

	await state.update_data(state_context_message_id=msg_id)



