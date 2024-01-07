from dataclasses import dataclass
from typing import Optional

from environs import Env


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str
    driver: str
    port: int = 5432

    @staticmethod
    def from_env(env: Env):
        host = env.str("DB_HOST")
        password = env.str("DB_PASSWORD")
        user = env.str("DB_USERNAME")
        database = env.str("DB_DATABASE")
        driver = env.str("DB_DRIVER")
        port = env.int("DB_PORT")
        return DbConfig(
            host=host, password=password, user=user, database=database, port=port, driver=driver
        )


@dataclass
class BotConfig:
    token: str
    admin_ids: list[int]

    @staticmethod
    def from_env(env: Env):
        token = env.str("BOT_TOKEN")
        admin_ids = list(map(int, env.list("ADMINS")))
        return BotConfig(token=token, admin_ids=admin_ids)


@dataclass
class Config:
    bot: BotConfig
    db: Optional[DbConfig] = None


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        bot=BotConfig.from_env(env),
        db=DbConfig.from_env(env)
    )
