import logging

from glob import glob
from pathlib import Path
from typing import Any
from yaml import load, CLoader

from omsu_bot.utils import pget

default_language = "ru"
logger = logging.getLogger(__name__)
lang = dict()

for path in glob("./lang/*.yml"):
	with open(path, encoding="utf-8") as f:
		lang_name = Path(path).stem
		try:
			lang[lang_name] = load(f, Loader=CLoader)
		except Exception as e:
			logging.error(f"Error ocurred while loading language \"{lang_name}\"", e, stack_info=True)

def phrase(ref: str) -> Any | str:
	return pget(lang, ref) or (pget(lang, ref) if ref[:ref.find("/")] != default_language else ref)