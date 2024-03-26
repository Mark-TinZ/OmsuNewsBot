import time
import environs

from environs import Env
from yaml import load, CLoader
from dataclasses import dataclass
from typing import Optional, Union
from datetime import date, datetime


@dataclass
class LogConf:
    level: str
    folder: str
    format: str

    @staticmethod
    def from_yaml(yaml: dict) -> "LogConf":
        level   = yaml["level"]
        folder  = yaml["folder"]
        format  = yaml["format"]
        
        # An instance of LogConf is created using the retrieved values and returned.
        return LogConf(level=level, folder=folder, format=format)


@dataclass
class DbConf:
    host: str
    password: str
    user: str
    database: str
    driver: str
    port: int = 5432
    echo: bool = False

    @staticmethod
    def from_yaml(yaml: dict) -> "DbConf":
        host        = yaml["connect"]["host"]
        host        = yaml["connect"]["host"]
        password    = yaml["connect"]["password"]
        user        = yaml["connect"]["user"]
        database    = yaml["connect"]["database"]
        driver      = yaml["connect"]["driver"]
        port        = yaml["connect"]["port"]
        echo        = yaml["echo"]

        # An instance of DbConf is created using the retrieved values and returned.
        return DbConf(
            host=host, password=password, user=user, database=database, port=port, driver=driver, echo=echo
        )


@dataclass
class BotConf:
    token: str
    admin_ids: list[Union[int, str]]
    timezone: str
    academic_start: str

    @staticmethod
    def from_yaml(yaml: dict) -> "BotConf":
        token       = yaml["token"]
        admin_ids   = yaml["admin_ids"]
        timezone    = yaml["timezone"]
        academic_start = datetime.strptime(yaml["academic_start"], "%d.%m.%Y").date()

        # An instance of BotConf is created using the retrieved values and returned.
        return BotConf(
            token=token, admin_ids=admin_ids, timezone=timezone, academic_start=academic_start
        )


@dataclass
class Config:
    bot: BotConf
    db: DbConf
    logger: LogConf


def load_config(path: str) -> Config:
    env = Env()
	
    env.read_env(path, override=True)

    return Config(
        bot     = BotConf(),
        db      = DbConf(),
        logger  = LogConf()
    )
