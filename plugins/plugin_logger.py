"""
PluginLogger - Logger especializado para plugins
Proporciona logging consistente y rastreable para todos los plugins.
"""
from core.logging import logger as app_logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plugins.plugin_manager import Plugin


class PluginLogger:
    """Logger especializado para plugins que añade contexto automático."""
    
    def __init__(self, plugin_name: str):
        """
        Inicializa el logger de plugin.
        
        Args:
            plugin_name: Nombre del plugin (automáticamente prefijado en logs)
        """
        self.plugin_name = plugin_name
        self._base_logger = app_logger
    
    def _format_message(self, message: str) -> str:
        """Añade el nombre del plugin al mensaje."""
        return f"[{self.plugin_name}] {message}"
    
    def error(self, message: str, exc_info: bool = False) -> None:
        """Log de error con contexto del plugin."""
        self._base_logger.error(self._format_message(message), exc_info=exc_info)
    
    def warning(self, message: str) -> None:
        """Log de advertencia con contexto del plugin."""
        self._base_logger.warning(self._format_message(message))
    
    def info(self, message: str) -> None:
        """Log informativo con contexto del plugin."""
        self._base_logger.info(self._format_message(message))
    
    def debug(self, message: str) -> None:
        """Log de debug con contexto del plugin."""
        self._base_logger.debug(self._format_message(message))
    
    def exception(self, message: str) -> None:
        """Log de excepción con traceback completo."""
        self._base_logger.exception(self._format_message(message))
    
    def lifecycle(self, stage: str) -> None:
        """Log de ciclo de vida del plugin (inicialización, limpieza, etc)."""
        self.info(f">>> {stage.upper()}")