import time
import asyncio
import logging
import aiogram

from typing import Any
from aiogram.fsm.context import FSMContext

logger = logging.getLogger()

async def remove_context(state: FSMContext, tg: aiogram.Bot):
	data = await state.get_data()

	msg_id = data.get("context_message_id", None)

	if msg_id:
		del data["context_message_id"]
		update = state.set_data(data)

		chat_id = state.key.chat_id

		try:
			await tg.edit_message_reply_markup(
				chat_id=chat_id,
				message_id=msg_id
			)
		except Exception: pass
		
		await update

async def register_context(state: FSMContext, message: aiogram.types.Message | int, tg: aiogram.Bot = None, safe: bool = False):
	if not tg:
		tg = message.bot
	
	if not safe:
		await remove_context(state, tg)

	msg_id = message if isinstance(message, int) else message.message_id

	await state.update_data(context_message_id=msg_id)


async def drop_context(state: FSMContext):
	data = await state.get_data()
	try:
		del data["context_message_id"]
		state.set_data(data)
	except Exception: pass



# freq: частота отправки, при которой будет записываться счётчик
# count: предел счётчика, после которого выдаётся задержка
# delay: кол-во секунд задержки, после переполнения счётчика
async def throttling_assert(state: FSMContext, freq: float = 2.0, count: int = 3, delay: float = 5.0, key: str = "main", sleep: bool = True) -> bool:
	data = await state.get_data()

	index = "throttling_"+key
	block_index = index+"_block"
	count_index = index+"_count"

	if data.get(block_index, False):
		return True

	now = time.time()
	last = data.get(index, 0)

	if now > last + freq:
		data[index] = now
		try:
			del data[count_index]
		except KeyError: pass
		
		await state.set_data(data)
		return False
	
	total_count = data.get(count_index, 0)
	if total_count < count:
		data[count_index] = total_count + 1
		data[index] = now
		await state.set_data(data)
		return False
	
	data[block_index] = True
	await state.set_data(data)
	
	if sleep:
		await asyncio.sleep(delay)

		data = await state.get_data()
		data[index] = time.time()

		try:
			del data[block_index]
			# del data[count_index]
		except KeyError: pass

		await state.set_data(data)
		return False
	
	return True

def rget(d: dict, *keys, exc=False) -> Any | None:
	try:
		target = d
		try:
			for k in keys: target = target[k]
			return target

		except KeyError:
			logger.warning(f"Could not find key {keys} in {d}")
			return None
	except Exception as e:
		logger.warning("Could not get value from dict")
		if exc: raise e

def pget(d: dict, path: str, exc=False) -> Any | None:
	return rget(d, *(path.split("/")), exc=False)




