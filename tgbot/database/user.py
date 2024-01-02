from tgbot.database.postgresql import database


async def select_user(**kwargs) -> None:
    async with database as db:
        sql = "SELECT * FROM users WHERE"
        sql, parameters = db.format_args(sql, kwargs)

        return await db.pool.fetchrow(sql, *parameters)

async def add_user(tg_id: int, role: str, course: int, group: str) -> None:
    async with database as db:
        sql = "INSERT INTO users (tg_id, role, course, \"group\") VALUES($1, $2, $3, $4)"
        await db.pool.execute(sql, tg_id, role, course, group)