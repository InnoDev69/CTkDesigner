import configparser
import os

class ConfigManager:
    """
    Módulo de configuración basado en configparser.
    Permite cargar, modificar y guardar configuraciones en un archivo .ini.
    """
    def __init__(self, filename="config.ini"):
        """
        Inicializa la clase ConfigManager.
        Si el archivo de configuración no existe, crea uno con valores predeterminados.
        
        :param filename: Nombre del archivo de configuración.
        """
        self.filename = filename
        self.config = configparser.ConfigParser()
        
        if not os.path.exists(self.filename):
            self._create_default_config()
        else:
            self.load_config()
            self.set("General", "first_init", False)

    def _create_default_config(self):
        """
        Crea una configuración predeterminada si el archivo no existe.
        """
        self.config["General"] = {
            "language": "es",
            "theme": "light",
            "first_init": True,
        }
        self.save_config()

    def load_config(self):
        """
        Carga la configuración desde el archivo .ini.
        """
        self.config.read(self.filename)

    def get(self, section, option, fallback=None):
        """
        Obtiene un valor de la configuración.
        
        :param section: Sección del archivo .ini.
        :param option: Opción dentro de la sección.
        :param fallback: Valor predeterminado en caso de que no exista la opción.
        :return: Valor de la opción especificada.
        """
        return self.config.get(section, option, fallback=fallback)

    def set(self, section, option, value):
        """
        Establece un valor en la configuración.
        
        :param section: Sección del archivo .ini.
        :param option: Opción dentro de la sección.
        :param value: Valor a establecer.
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, str(value))
        self.save_config()

    def save_config(self):
        """
        Guarda la configuración en el archivo .ini.
        """
        with open(self.filename, "w") as configfile:
            self.config.write(configfile)