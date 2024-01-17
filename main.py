import os
import asyncio
import logging

import betterlogging as bl
from datetime import datetime

from omsu_bot import OMSUBot
from omsu_bot.config import load_config


def setup_logging() -> None:
	log_level = logging.INFO
	bl.basic_colorized_config(level=log_level)

	logs_folder = 'logs'
	os.makedirs(logs_folder, exist_ok=True)
	log_format = "%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s"
	file_handler = logging.FileHandler(f"{logs_folder}/log-{datetime.now().strftime('%Y-%m-%d')}.log")
	file_handler.setFormatter(logging.Formatter(log_format))

	logging.basicConfig(
		level=log_level,
		format=log_format,
		handlers=[file_handler] 
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
