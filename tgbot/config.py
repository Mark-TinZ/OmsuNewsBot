import asyncio
from dataclasses import dataclass
from typing import Optional

from environs import Env




@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str
    port: int

    @staticmethod
    def from_env(env: Env):
        host = env.str("PG_HOST")
        password = env.str("PG_PASS")
        user = env.str("PG_USER")
        database = env.str("DB_NAME")
        port = env.int("PG_PORT")

        return DbConfig(
            host=host, password=password, user=user, database=database, port=port
        )


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]

    @staticmethod
    def from_env(env: Env):
        token = env.str("BOT_TOKEN")
        admin_ids = list(map(int, env.list("ADMINS")))

        return TgBot(token=token, admin_ids=admin_ids)


@dataclass
class Config:
    tg_bot: TgBot
    db: Optional[DbConfig] = None


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot.from_env(env),
        db=DbConfig.from_env(env)
    )
