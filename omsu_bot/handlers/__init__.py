from aiogram import Router


<<<<<<< HEAD
=======
# from aiogram.filters import Command
# from aiogram.fsm.context import FSMContext
# from aiogram.types import Message


>>>>>>> b3cbe8f121d82c6ca395df027451653658db9799
class Handler:
	bot = None

	async def enable(self, bot):
		self.bot = bot

	async def disable(self):
		self.bot = None


<<<<<<< HEAD
=======

>>>>>>> b3cbe8f121d82c6ca395df027451653658db9799
class RouterHandler(Handler):
	def __init__(self, router: Router = None) -> None:
		super().__init__()
		self.router = router or Router()

	async def enable(self, bot):
		await super().enable(bot)
		bot.dispatcher.include_router(self.router)

