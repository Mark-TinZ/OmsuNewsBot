from typing import Any
from aiogram.filters import BaseFilter
from aiogram.types import Message

class MainFilter():
	def __init__(self, allow_groups: None | bool = False) -> None:
		self.allow_groups = allow_groups or False
	
	def __call__(self, msg: Message) -> Any:
		return self.allow_groups or msg.chat.type == "private"



# class ChatTypeFilter(BaseFilter):
#     def __init__(self, chat_type: Union[str, list]):
#         self.chat_type = chat_type

#     async def __call__(self, message: Message) -> bool:
#         if isinstance(self.chat_type, str):
#             return message.chat.type == self.chat_type
#         else:
#             return message.chat.type in self.chat_type

