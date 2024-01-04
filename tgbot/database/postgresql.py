import asyncio
from asyncio import get_event_loop

import asyncpg
from asyncpg.pool import Pool


class Database():
    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self.loop = loop
        self.pool = None

    async def connect(self, user, password, host, port, database) -> None:
        self.pool = await asyncpg.create_pool(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += ' '
        sql += ' AND '.join([
            f'{item} = ${num}' for num, item in enumerate(parameters, start=1)
        ])
        return sql, tuple(parameters.values())


loop = get_event_loop()
db = Database(loop)
