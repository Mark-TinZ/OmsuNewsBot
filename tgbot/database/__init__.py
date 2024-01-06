import sqlalchemy as sa
import sqlalchemy.orm as sorm
import tgbot.database.models as models

# class database SQLAlchemy
class Database():  
	def __init__(self, driver: str, username: str, password: str, host: str, port: int, database: str) -> None:
		self.url = sa.URL(driver, username, password, host, port, database, dict())
		self.engine = sa.create_engine(self.url)

		self.create_all_metadata()

	def create_all_metadata(self):
		models.metadata.create_all(self.engine)


