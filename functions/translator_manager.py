from translations.translator import *
from translations.translations import *
from config.config_manager import ConfigManager

config_manager = ConfigManager()
translator = Translator(config_manager.get("General", "language"))
translator.load_translations(translations)