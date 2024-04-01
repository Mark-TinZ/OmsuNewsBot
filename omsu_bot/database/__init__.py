import sqlalchemy as sa
import sqlalchemy.orm as sorm
import omsu_bot.database.models as models

from omsu_bot.config import DbConf


class Database:
	_session: sorm.Session | None = None
	def __init__(self, db: DbConf) -> None:
		self.url = sa.URL(db.driver, db.user, db.password, db.host, db.port, db.database, dict())
		self.engine = sa.create_engine(self.url, echo=db.echo)
	
	def is_online(self) -> sorm.Session | None:
		return (self._session)

	@property
	def session(self) -> sorm.Session | None:
		return self._session
	
	async def launch(self) -> None:
		await self.create_all_metadata()

		sess = sorm.Session(self.engine, expire_on_commit=True)
		self._session = sess
		self.connection = sa.Connection(self.engine)
		self.connection = self.engine.connect

	async def shutdown(self) -> None:
		if self._session:
			self._session.close()
			self._session = None

	async def create_all_metadata(self) -> None:
		models.metadata.create_all(self.engine)


