import asyncio
import logging

import betterlogging as bl

from omsu_bot import OMSUBot
from omsu_bot.config import load_config


def setup_logging() -> None:
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


async def main() -> None:
    setup_logging()

    config = load_config(".env")

    bot = OMSUBot(config)
    await bot.launch()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
