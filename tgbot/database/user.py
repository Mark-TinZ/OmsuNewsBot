from tgbot.database.postgresql import database


async def select_user(**kwargs):
    async with database as db:
        sql = "SELECT * FROM users WHERE"
        sql, parameters = db.format_args(sql, kwargs)

        return await db.pool.fetchrow(sql, *parameters)
