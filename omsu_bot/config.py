from yaml import load, CLoader
from dataclasses import dataclass
from typing import Union
from datetime import datetime


@dataclass
class BotConf:
    token: str

    @staticmethod
    def from_yaml(yaml: dict) -> "BotConf":
        token = yaml["token"]

        return BotConf(
            token=token
        )
<<<<<<< HEAD


=======
  
>>>>>>> b3cbe8f121d82c6ca395df027451653658db9799
@dataclass
class MainConf:
    parse_mode: str
    timezone: str
    academic_start: str
    admin_ids: list[Union[int, str]]

    @staticmethod
    def from_yaml(yaml: dict) -> "MainConf":
        timezone        = yaml["timezone"]
        admin_ids       = yaml["admin_ids"]
        parse_mode      = yaml["parse_mode"]
        academic_start  = datetime.strptime(yaml["academic_start"], "%d.%m.%Y").date()

<<<<<<< HEAD
=======
        # An instance of BotConf is created using the retrieved values and returned.
>>>>>>> b3cbe8f121d82c6ca395df027451653658db9799
        return MainConf(
            admin_ids=admin_ids, timezone=timezone, parse_mode=parse_mode, academic_start=academic_start
        )

<<<<<<< HEAD

=======
>>>>>>> b3cbe8f121d82c6ca395df027451653658db9799
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
        host     = yaml["connect"]["host"]
        host     = yaml["connect"]["host"]
        password = yaml["connect"]["password"]
        user     = yaml["connect"]["user"]
        database = yaml["connect"]["database"]
        driver   = yaml["connect"]["driver"]
        port     = yaml["connect"]["port"]
        echo     = yaml["echo"]

<<<<<<< HEAD
=======
        # An instance of DbConf is created using the retrieved values and returned.
>>>>>>> b3cbe8f121d82c6ca395df027451653658db9799
        return DbConf(
            host=host, password=password, user=user, database=database, port=port, driver=driver, echo=echo
        )

<<<<<<< HEAD

=======
>>>>>>> b3cbe8f121d82c6ca395df027451653658db9799
@dataclass
class LogConf:
    level: str
    folder: str
    format: str

    @staticmethod
    def from_yaml(yaml: dict) -> "LogConf":
        level  = yaml["level"]
        folder = yaml["folder"]
        format = yaml["format"]
        
<<<<<<< HEAD
        return LogConf(level=level, folder=folder, format=format)


=======
        # An instance of LogConf is created using the retrieved values and returned.
        return LogConf(level=level, folder=folder, format=format)

>>>>>>> b3cbe8f121d82c6ca395df027451653658db9799
@dataclass
class Config:
    bot: BotConf
    main: MainConf
    db: DbConf
    logger: LogConf


def load_config(path: str) -> Config:
    with open(path, encoding="utf-8") as file:
        config: dict = load(file, Loader=CLoader)
    
    bot_cfg: dict   = config["bot"]
    main_cfg: dict  = config["maintenance"]
    db_cfg: dict    = config["database"]
    log_cfg: dict   = config["logging"]

    return Config(
        bot    = BotConf.from_yaml(bot_cfg),
        main   = MainConf.from_yaml(main_cfg),
        db     = DbConf.from_yaml(db_cfg),
        logger = LogConf.from_yaml(log_cfg)
    )