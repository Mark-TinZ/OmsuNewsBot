from dataclasses import dataclass
import time
from typing import Optional, Union
from datetime import date, datetime
from environs import Env
import environs


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str
    driver: str
    port: int = 5432

    @staticmethod
    def from_env(env: Env) -> "DbConfig":
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
    admin_ids: list[Union[int, str]]
    timezone: str

    @staticmethod
    def from_env(env: Env) -> "BotConfig":
        token = env.str("BOT_TOKEN")
        admin_ids = list(map(int, env.list("ADMINS")))
        timezone = env.str("TIMEZONE")
        return BotConfig(token=token, admin_ids=admin_ids, timezone=timezone) # type: ignore


@dataclass
class ScheduleConfig():
    academic_start: date
    @staticmethod
    def from_env(env: Env) -> "ScheduleConfig":
        academic_start = datetime.strptime(env.str("SCH_ACADEMIC_START"), "%d.%m.%Y").date()
        print(academic_start)
        return ScheduleConfig(academic_start=academic_start)


@dataclass
class Config:
    bot: BotConfig
    schedule: ScheduleConfig
    db: Optional[DbConfig] = None


def load_config(path: str) -> Config:
    env = Env()
	
    env.read_env(path, override=True)

    return Config(
        bot=BotConfig.from_env(env),
        db=DbConfig.from_env(env),
        schedule=ScheduleConfig.from_env(env)
    )
