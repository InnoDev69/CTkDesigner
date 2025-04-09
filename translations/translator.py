class Translator:
    def __init__(self, default_language="en"):
        self.languages = {"es": {}, "en": {}}
        self.current_language = default_language

    def load_translations(self, translations):
        """
        Carga un diccionario de traducciones.
        Ejemplo: {"es": {"hello": "Hola"}, "en": {"hello": "Hello"}}
        """
        for lang, texts in translations.items():
            self.languages[lang] = texts

    def set_language(self, language:str):
        if language in self.languages:
            self.current_language = language
        else:
            raise ValueError(f"Idioma no soportado: {language}")

    def translate(self, key):
        return self.languages[self.current_language].get(key, key)
    
    def translate_with_vars(self, key, variables):
        """
        Traduce una cadena con variables.
        
        :param key: La clave de la cadena de formato en el diccionario de traducciones.
        :param variables: Un diccionario de variables para formatear la cadena.
        :return: La cadena traducida y formateada.
        """
        translated_string = self.translate(key)
        return translated_string.format(**variables)
    
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
