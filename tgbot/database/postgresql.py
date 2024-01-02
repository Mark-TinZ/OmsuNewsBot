import asyncio
from asyncio import get_event_loop

import asyncpg

from tgbot.config import load_config


class Database:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.pool = None

    async def __aenter__(self):
        config = load_config(".env")

        self.pool = await asyncpg.create_pool(
            user=config.db.user,
            password=config.db.password,
            host=config.db.host,
            port=config.db.port,
            database=config.db.database
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.pool.close()

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += ' '
        sql += ' AND '.join([
            f'{item} = ${num}' for num, item in enumerate(parameters, start=1)
        ])
        return sql, tuple(parameters.values())


loop = get_event_loop()
database = Database(loop)


db = Database(asyncio.get_event_loop())
