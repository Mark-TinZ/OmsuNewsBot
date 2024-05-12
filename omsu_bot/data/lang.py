import os
import logging

from glob import glob
from pathlib import Path
from typing import Any
from yaml import load, CLoader
from dataclasses import dataclass

from omsu_bot.utils import pget

default_language = "ru"
logger = logging.getLogger(__name__)
lang = dict()

# @dataclass
# class ExtLang(Exception):
#     def directory_notfount():
#         logger.critical("directory notfount")

# class Localization:
#     def __init__(self, base_dir: str = "lang", default_lang: str = "ru")  -> None:
#         self.base_dir = base_dir
#         self.default_lang = default_lang
#         self.translations = self._load_translations()

#     def _load_translations(self) -> dict:
#         translations = dict()
#         if not os.path.isdir(self.base_dir):
#             raise ExtLang.directory_notfount()
        
#         for lang_file in os.listdir(self.base_dir):
#             if lang_file.endswith(".yaml") or lang_file.endswith(".yml"):
#                 lang_code, _ = os.path.splitext(lang_file)
#                 with open(os.path.join(self.base_dir, lang_file), "r", encoding="utf-8") as file:
#                     lang_data = load(file, Loader=CLoader)
#                     translations[lang_code] = lang_data
#         logger.info("Localization setup: Done")
#         return translations

#     def get_translation(self, lang_code) -> dict:
#         if lang_code is None:
#             lang_code = self.default_lang
#         return self.translations.get(lang_code, self.translations.get(self.default_lang))

#     def __getitem__(self, key):
#         return self.get_translation(key)

for path in glob("./lang/*.yml"):
	with open(path, encoding="utf-8") as f:
		lang_name = Path(path).stem
		try:
			lang[lang_name] = load(f, Loader=CLoader)
		except Exception as e:
			logging.error(f"Error ocurred while loading language \"{lang_name}\"", e, stack_info=True)

def phrase(ref: str) -> Any | str:
	return pget(lang, ref) or (pget(lang, ref) if ref[:ref.find("/")] != default_language else ref)


# user_greetings = (
#     "👋 Приветствуем тебя в удобном <b>неофициальном</b> Telegram-боте для студентов и преподавателей!\n\n\n"

#     "📅 <b>Основные возможности бота:</b>\n\n"
    
# 	"📚 Просматривай расписание пар для своей группы.\n"
    
# 	"🕒 Получай уведомления о предстоящих занятиях.\n\n"
    
#     "🔍 <i>Этот бот станет незаменимым помощником не только для студентов, но и для преподавателей. "
#     "Удобство и оперативность в одном месте!</i> 💼🎓\n\n"
    
#     "Присоединяйся и будь в курсе своего учебного процесса! 🚀"
# )

# user_registration_warning = (
#     "🤖 Привет! Бот нуждается в данных о твоей группе, курсе и идентификаторе Telegram для корректной работы.\n"
# 	"Подтверди свое согласие, чтобы бот мог предоставить тебе все возможности.\n"
# 	"Без этих данных он не сможет работать. 📊✅"
# )

# user_registration_eula = (
#     "📝 <b>Пользовательское соглашение:</b>\n"
	
# 	"Предоставление данных:\n"
	
# 	"При использовании функционала Telegram-бота, "
# 	"вы соглашаетесь предоставить боту информацию о своем курсе и группе для корректного отображения расписания.\n"
	
# 	"Введенные вами данные будут сохранены в нашей базе данных и "
# 	"использоваться исключительно для предоставления вам персонализированного расписания.\n"
	
# 	"Конфиденциальность:\n"
	
# 	"Ваши персональные данные будут обрабатываться с соблюдением принципов конфиденциальности и безопасности. "
# 	"Мы не передаем вашу информацию третьим лицам.\n"
	
# 	"Безопасность:\n"
# 	"Мы прилагаем все усилия для обеспечения безопасности ваших данных. Однако, помните, "
# 	"что безопасность в интернете не гарантирована, и вы также несете ответственность за сохранность своих учетных данных.\n"
	
# 	"Отказ от ответственности:\n"
	
# 	"Мы не несем ответственности за любые непредвиденные сбои в работе бота или потерю данных. "
# 	"Использование бота на ваш собственный риск.\n"
	
# 	"Согласие с условиями:\n"
	
# 	"Используя функционал бота, вы подтверждаете свое согласие с вышеуказанными условиями использования."
# )

# user_moderator_description = (
#     "*🛠️ Модераторская роль:*\n"
# 	"Эксклюзивный доступ к изменению расписания пар 🗓️.\n"
# 	"Обеспечивает легкость и удобство в поддержании актуальности учебных данных 📚.\n"
# 	"Оперативные изменения для максимального комфорта и актуальности информации ✨."
# )

# user_menu_description = "Чем могу помочь?"

# user_error_database_connection = "В данный момент по техническим неполадкам бот недоступен..."

# user_error_database_logic = "Логическое исключение, запись в бд повреждена\n\nОбратитесь к администратору бота..."

# user_error_try_again = "Произошла ошибка, пожалуйста, попробуйте еще раз."

# user_error_auth_unknown = (
#     "Вы не зарегистрированы!\n\n"
#     "Для регистрации введите комманду /start"
# )

# user_error_auth_unknown_group = (
#     "Вы не зарегистрированы!\n\n"
#     "Для регистрации введите комманду /start в личном чате с ботом."
# )

# user_about = (
# 	"Привет! 👋 Добро пожаловать в *неофициального* Telegram-бота! 🤖 Здесь ты можешь:\n\n"
# 	"📅 Просматривать расписание для своей группы.\n"
# 	"🔔 Получать уведомления о завтрашних занятиях.\n\n"
# 	"Этот бот пригодится не только студентам, но и преподавателям. 📚✨"
# )

# user_about_idea = (
#     "😎 Предложите свою идею)\n"
#     "P.s. Пишите одним сообщением до 4 тыс. символов."
# )

# user_about_idea_answer = (
#     "Отлично! Мы получили ваше сообщение."
# )

# user_about_report = (
#     "🚨 Сообщите о проблеме.\n"
#     "Мы готовы помочь в ее решении! Пожалуйста, сообщите нам подробности о возникшей ошибке, "
#     "чтобы мы могли оперативно исправить ситуацию. Спасибо за ваше терпение и содействие!\n"
#     "P.s. Пишите одним сообщением до 4 тыс. символов."
# )
# user_about_idea_error_len = (
#     "Ваше сообщение превышает установленный лимит или вызывает ошибку."
# )

# month_map = {
#     1: "Январь",
#     2: "Февраль",
#     3: "Март",
#     4: "Апрель",
#     5: "Май",
#     6: "Июнь",
#     7: "Июль",
#     8: "Август",
#     9: "Сентябрь",
#     10: "Октябрь",
#     11: "Ноябрь",
#     12: "Декабрь"
# }

# weekday_map = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

# academic_weeks = "Сейчас идет {academic_week}-я учебная неделя"

