import asyncio

import asyncpg

from tgbot.config import load_config


class Database:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        config = load_config(".env")

        self.pool = loop.run_until_complete(
            asyncpg.create_pool(
                user=config.db.user,
                password=config.db.password,
                host=config.db.host,
                port=config.db.port
            )
        )


db = Database(asyncio.get_event_loop())
