import logging

from tgbot.database.postgresql import db

user_map = dict()


class User:
    def __init__(self, tg_id: int, role: str, course: int, group: str, settings: dict, name: str) -> None:
        self.tg_id = tg_id
        self.role = role
        self.course = course
        self.group = group
        self.is_existing = True

        user_map[tg_id] = self

    def set_role(self, role) -> None:
        pass

    def set_group(self, group):
        pass

    def is_valid(self):
        return self.is_existing

    def release(self):
        if user_map[self.tg_id] == self:
            del user_map[self.tg_id]
        self.is_existing = False


async def add_user(tg_id: int, role: str = "user", course: int = None, group: str = None) -> None:
    sql = "INSERT INTO users (tg_id, role, course, \"group\") VALUES($1, $2, $3, $4)"
    await db.pool.execute(sql, tg_id, role, course, group)


async def select_user(**kwargs) -> any:
    sql = "SELECT * FROM users WHERE"

    formatted_sql, parameters = db.format_args(sql, kwargs)
    logging.debug("Form: {}, Params: {}", formatted_sql, parameters)
    row = (await db.pool.fetchrow(formatted_sql, *parameters))

    return row


async def create_user(tg_id: int, role: str = "user", course: int = None, group: str = None, settings: dict = None,
                      name: str = None) -> User:
    await add_user(tg_id, role, course, group)
    return User(tg_id, role, course, group, settings, name)


async def get_user(tg_id: int) -> User | None:
    user: User = user_map[tg_id]

    if not user:
        row = select_user(tg_id=tg_id)
        if row:
            user = User(tg_id, row[1], row[2], row[3], row[4], row[5])

    return user
