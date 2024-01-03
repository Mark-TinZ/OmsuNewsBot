from tgbot.database.postgresql import db

user_map = dict()


class User:
    def __init__(self, tg_id: int, role: str, course: int, group: str) -> None:
        self.tg_id = tg_id
        self.role = role
        self.course = course
        self.group = group

    def set_role(self, role) -> None:
        pass


async def add_user(tg_id: int, role: str, course: int, group: str) -> None:
    sql = "INSERT INTO users (tg_id, role, course, \"group\") VALUES($1, $2, $3, $4)"
    await db.pool.execute(sql, tg_id, role, course, group)


async def select_user(**kwargs) -> any:
    sql = "SELECT * FROM users WHERE"

    formatted_sql, parameters = db.format_args(sql, kwargs)
    print(formatted_sql, parameters)
    row = (await db.pool.fetchrow(formatted_sql, *parameters))

    return row

async def get_user(tg_id: int) -> User|None:
    user = user_map[tg_id]

    if not User:
        row = select_user()
    


