from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from omsu_bot.config import Config
from omsu_bot.database import Database
from omsu_bot.handlers import Handler
import omsu_bot.handlers


class OMSUBot:
    def __init__(self, cfg: Config):
        self.config = cfg

        self.fsm_storage = get_fsm_storage(cfg)

        tg = Bot(token=cfg.bot.token, parse_mode="HTML")
        dp = Dispatcher(storage=self.fsm_storage)

        self.tg = tg
        self.dispatcher = dp

        self.db = Database(cfg.db.driver, cfg.db.user, cfg.db.password, cfg.db.host, cfg.db.port,
                           cfg.db.database)

        handler_list = []
        for handler in omsu_bot.handlers.handlers:
            handler_list.append(handler())

        self.handlers = handler_list

    async def launch(self):
        self.db.create_all_metadata()

        for h in self.handlers:
            h.enable(self)

        tg = self.tg
        await tg.delete_webhook(drop_pending_updates=True)
        await self.dispatcher.start_polling(tg)


def get_fsm_storage(cfg: Config) -> MemoryStorage:
    return MemoryStorage()
