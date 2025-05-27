import json
import os
from pathlib import Path
from functools import lru_cache
import logging

class Translator:
    def __init__(self, default_language="en"):
        self.languages = {"es": {}, "en": {}}
        self.current_language = default_language
        self._load_json_translations()
    
    def _load_json_translations(self):
        """Load translations from JSON files"""
        try:
            locale_dir = Path(__file__).parent / "locales"
            if not locale_dir.exists():
                logging.warning(f"Locales directory not found at {locale_dir}")
                return
                
            for file in locale_dir.glob("*.json"):
                lang_code = file.stem
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        if lang_code not in self.languages:
                            self.languages[lang_code] = {}
                        self.languages[lang_code].update(json.load(f))
                    logging.info(f"Loaded translations for {lang_code} from {file.name}")
                except json.JSONDecodeError as e:
                    logging.error(f"Invalid JSON in {file.name}: {e}")
                except Exception as e:
                    logging.error(f"Error loading {lang_code}: {e}")
                    
        except Exception as e:
            logging.error(f"Error accessing locale directory: {e}")

    def load_translations(self, translations):
        """Mantiene compatibilidad con el sistema antiguo"""
        for lang, texts in translations.items():
            if lang not in self.languages:
                self.languages[lang] = {}
            self.languages[lang].update(texts)

    @lru_cache(maxsize=1000)
    def get(self, key: str, **kwargs) -> str:
        """
        Obtiene traducción usando notación de punto o clave directa
        Ejemplo: get("menu.file.new") o get("NEW_PROYECT")
        """
        try:
            # Primero intenta con notación de punto
            if "." in key:
                return self._get_nested(key, **kwargs)
            
            # Si no, usa el sistema antiguo
            translated = self.languages[self.current_language].get(key, key)
            
            # Aplica las variables si existen
            if kwargs and "{" in translated:
                try:
                    return translated.format(**kwargs)
                except KeyError as e:
                    logging.warning(f"Missing variable in translation: {e}")
                    return translated
            return translated
            
        except Exception as e:
            logging.warning(f"Translation error for key '{key}': {e}")
            return key

    def _get_nested(self, key: str, **kwargs) -> str:
        """Obtiene traducción usando notación de punto"""
        keys = key.split('.')
        value = self.languages[self.current_language]
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, k)
            else:
                return key
                
        return value.format(**kwargs) if kwargs else value

    # Mantiene métodos existentes para compatibilidad
    def translate(self, key):
        return self.languages[self.current_language].get(key, key)
    
    def translate_with_vars(self, key, variables):
        """
        Traduce una cadena con variables y proporciona información de debug
        Args:
            key: Clave de traducción
            variables: Diccionario de variables para formatear
        """
        try:
            translated_string = self.translate(key)
            logging.debug(f"Traduciendo '{key}' -> '{translated_string}'")
            logging.debug(f"Variables proporcionadas: {variables}")
            
            if "{" not in translated_string:
                logging.warning(f"La cadena traducida no contiene marcadores de formato: '{translated_string}'")
                return translated_string
                
            # Verificar que todas las variables necesarias están presentes
            required_vars = [name.split('}')[0] for name in translated_string.split('{')[1:]]
            missing_vars = [var for var in required_vars if var not in variables]
            
            if missing_vars:
                logging.error(f"Faltan variables requeridas: {missing_vars}")
                return translated_string
                
            result = translated_string.format(**variables)
            logging.debug(f"Resultado final: '{result}'")
            return result
            
        except KeyError as e:
            logging.error(f"Error de variable faltante: {e}")
            return translated_string
        except Exception as e:
            logging.error(f"Error al traducir '{key}' con variables {variables}: {e}")
            return key
    
    def set_language(self, language:str):
        if language not in self.languages:
            raise ValueError(f"Idioma no soportado: {language}")
        self.current_language = language
        self.get.cache_clear()

    def find_key_by_value(self, target_value):
        """
        Encuentra la clave asociada a un valor específico en el idioma dado.
        """
        for language in ['en', 'es']:
            if language not in self.languages:
                raise ValueError(f"Idioma '{language}' no encontrado en las traducciones.")

            return next(
                (
                    key
                    for key, value in self.languages[language].items()
                    if value == target_value
                ),
                None,
            )
