import os
import asyncio
import logging

import betterlogging as bl
from datetime import datetime
from yaml import load, CLoader
from logging.handlers import TimedRotatingFileHandler

from omsu_bot import OMSUBot
from omsu_bot.config import load_config

# Set up logger
def setup_logging(config) -> None:
	c_logging = config["logging"]
	
	level = logging.getLevelName(c_logging.get("level", "DEBUG"))
	bl.basic_colorized_config(level=level)

	folder = c_logging["folder"]
	os.makedirs(folder, exist_ok=True)
	formatter = logging.Formatter(c_logging["format"])
	
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
	with open("config.yaml", encoding="utf-8") as file:
		config: dict = load(file, Loader=CLoader)
	
	setup_logging(config)

	with open("secret.yaml", encoding="utf-8") as file:
		secret: sict = load(file, Loader=CLoader)

	bot = OMSUBot(config, secret)
	await bot.start()


if __name__ == '__main__':
	try:
		asyncio.run(main())
	except (KeyboardInterrupt, SystemExit):
		logging.error("Bot stopped!")
		logging.shutdown()
