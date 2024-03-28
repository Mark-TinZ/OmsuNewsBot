import os
import asyncio
import logging

import betterlogging as bl
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from omsu_bot import OMSUBot
from omsu_bot.config import Config, load_config

# Set up logger
def setup_logging(config: Config) -> None:
	logger = config.logger
	level = logging.getLevelName(logger.level)
	bl.basic_colorized_config(level=level)

	folder = logger.folder
	os.makedirs(folder, exist_ok=True)
	formatter = logging.Formatter(logger.format)
	
	handler = TimedRotatingFileHandler(f"{folder}/log-{datetime.now().strftime('%Y-%m-%d')}.log", when="D", backupCount=30)
	handler.setFormatter(formatter)

	root = logging.getLogger()
	root.setLevel(level)
	root.addHandler(handler)
	
	logging.basicConfig(
		level=level,
		format=formatter
	)

	root.info("Logging setup: Done")


async def main() -> None:
	config = load_config("config.yml")

	setup_logging(config)

	bot = OMSUBot(config)
	await bot.start()


if __name__ == '__main__':
	try:
		asyncio.run(main())
	except (KeyboardInterrupt, SystemExit):
		logging.error("Bot stopped!")
		logging.shutdown()
