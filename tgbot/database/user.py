import logging

from tgbot.database.postgresql import db

user_map = dict()


class User:
    def __init__(self, tg_id: int, role: str, course: int, group: str, settings: dict, name: str) -> None:
        self.tg_id = tg_id
        self.role = role
        self.course = course
        self.group = group
        self.is_removed = False
        self.is_released = False

        user_map[tg_id] = self

    async def set_role(self, role: str) -> None:
        return (await db.pool.execute("""UPDATE users SET role_id = $2 WHERE tg_id = $1 """, self.tg_id, role))

    async def set_group(self, group):
        return (await db.pool.execute("""UPDATE users SET group_id = $2 WHERE tg_id = $1 """, self.tg_id, group))
    
    async def get_tg_id(self):
        return self.tg_id

    def is_valid(self):
        return not self.is_removed and not self.is_released

    def release(self):
        if user_map[self.tg_id] == self:
            del user_map[self.tg_id]
        self.is_released = True


async def add_user(tg_id: int, role: str = "user", course: int = None, group: str = None) -> None:
    sql = "INSERT INTO users (tg_id, role_id, course_number, group_id) VALUES($1, $2, $3, $4)"
    await db.pool.execute(sql, tg_id, role, course, group)


async def select_user(**kwargs) -> any:
    tg_id = kwargs.get('tg_id', None)
    if tg_id:
        user = user_map.get(tg_id, None)
        if user:
            return user
    
    sql = "SELECT * FROM users WHERE"

    formatted_sql, parameters = db.format_args(sql, kwargs)
    logging.debug("Form: {}, Params: {}", formatted_sql, parameters)
    row = (await db.pool.fetchrow(formatted_sql, *parameters))

    if not row:
        return

    tg_id = row[0]

    return user_map.get(tg_id, None) or User(tg_id, row[1], row[2], row[3], row[4], row[5])


async def create_user(tg_id: int, role: str = "user", course: int = None, group: str = None, settings: dict = None,
                      name: str = None) -> User:
    await add_user(tg_id, role, course, group)
    return User(tg_id, role, course, group, settings, name)

