from aiogram import Router


class Handler:
	bot = None

	async def enable(self, bot):
		self.bot = bot

	async def disable(self):
		self.bot = None

class RouterHandler(Handler):
	def __init__(self, router: Router = None) -> None:
		super().__init__()
		self.router = router or Router()

	async def enable(self, bot):
		await super().enable(bot)
		bot.dispatcher.include_router(self.router)

