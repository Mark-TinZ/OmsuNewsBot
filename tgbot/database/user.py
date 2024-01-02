from tgbot.database.postgresql import db


async def add_user(tg_id: int, role: str, course: int, group: str) -> None:
    sql = "INSERT INTO users (tg_id, role, course, \"group\") VALUES($1, $2, $3, $4)"
    await db.pool.execute(sql, tg_id, role, course, group)


async def select_user(**kwargs) -> any:
    sql = "SELECT * FROM users WHERE"
    formatted_sql, parameters = db.format_args(sql, kwargs)

    return await db.pool.fetchrow(formatted_sql, *parameters)
