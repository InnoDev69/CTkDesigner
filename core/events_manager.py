import logging
from typing import Callable, Dict, List

class EventManager:
    """Sistema de eventos para comunicación entre componentes de la aplicación."""
    
    def __init__(self, app):
        """
        Inicializa el EventManager.
        
        Args:
            app: La instancia principal de la aplicación
        """
        self.app = app
        self._listeners: Dict[str, List[Callable]] = {}
        self._event_history: List[tuple] = []
        
        logging.info("EventManager inicializado")
    
    def on(self, event: str, callback: Callable) -> None:
        """
        Registra un listener para un evento específico.
        
        Args:
            event: Nombre del evento (ej: "APP_READY", "WIDGET_ADDED")
            callback: Función a llamar cuando se dispare el evento
        """
        if event not in self._listeners:
            self._listeners[event] = []
        
        self._listeners[event].append(callback)
        logging.debug(f"Listener registrado para evento: {event}")
    
    def off(self, event: str, callback: Callable) -> None:
        """
        Desregistra un listener de un evento.
        
        Args:
            event: Nombre del evento
            callback: Función a remover
        """
        if event in self._listeners and callback in self._listeners[event]:
            self._listeners[event].remove(callback)
            logging.debug(f"Listener removido del evento: {event}")
    
    def emit(self, event: str, *args, **kwargs) -> None:
        """
        Dispara un evento y notifica a todos los listeners registrados.
        
        Args:
            event: Nombre del evento
            *args: Argumentos posicionales para pasar a los callbacks
            **kwargs: Argumentos nombrados para pasar a los callbacks
        """
        logging.info(f"Evento disparado: {event}")
        
        self._event_history.append((event, args, kwargs))
        
        if event in self._listeners:
            for callback in self._listeners[event]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logging.error(f"Error en callback para evento '{event}': {e}", exc_info=True)
    
    def get_event_history(self, limit: int = None) -> List[tuple]:
        """
        Obtiene el historial de eventos disparados.
        
        Args:
            limit: Número máximo de eventos a retornar
        
        Returns:
            Lista de tuplas (evento, argumentos, kwargs)
        """
        if limit:
            return self._event_history[-limit:]
        return self._event_history
    
    def clear_history(self) -> None:
        """Limpia el historial de eventos."""
        self._event_history.clear()
    
    def get_listeners(self, event: str = None) -> Dict:
        """
        Obtiene los listeners registrados.
        
        Args:
            event: Evento específico (opcional)
        
        Returns:
            Dict con los listeners
        """
        if event:
            return {event: self._listeners.get(event, [])}
        return self._listeners