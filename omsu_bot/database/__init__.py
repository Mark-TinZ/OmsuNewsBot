import sqlalchemy as sa
import sqlalchemy.orm as sorm
import omsu_bot.database.models as models


class Database:
	_session: sorm.Session | None = None
	def __init__(self, driver: str, username: str, password: str, host: str, port: int, database: str) -> None:
		self.url = sa.URL(driver, username, password, host, port, database, dict())
		self.engine = sa.create_engine(self.url)

	@property
	def session(self) -> sorm.Session | None:
		return self._session
	
	async def launch(self):
		await self.create_all_metadata()

		sess = sorm.Session(self.engine)
		self._session = sess # ?

	async def shutdown(self):
		if self._session:
			self._session.close()
			self._session = None

	async def create_all_metadata(self):
		models.metadata.create_all(self.engine)


