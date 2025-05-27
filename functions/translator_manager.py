from translations.translator import Translator
from translations.translations import translations
from config.config_manager import ConfigManager
import logging
from pathlib import Path

def initialize_translator():
    """Initialize the translator with both JSON and legacy translations"""
    try:
        config_manager = ConfigManager()
        default_language = config_manager.get("General", "language")
        
        # Create translator instance
        translator = Translator(default_language)
        
        # Load JSON translations first
        translator._load_json_translations()
        
        # Load legacy translations as fallback
        translator.load_translations(translations)
        
        logging.info(f"Translator initialized with language: {default_language}")
        return translator
        
    except Exception as e:
        logging.error(f"Error initializing translator: {e}")
        # Fallback to basic translator with English
        return Translator("en")

# Create global translator instance
translator = initialize_translator()