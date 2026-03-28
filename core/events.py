class AppEvents:
    """Constantes de eventos de la aplicación."""
    APP_READY = "APP_READY"                           # App lista para usar
    PLUGINS_INITIALIZED = "PLUGINS_INITIALIZED"       # Plugins inicializados
    WIDGET_ADDED = "WIDGET_ADDED"                     # Widget agregado
    WIDGET_DELETED = "WIDGET_DELETED"                 # Widget eliminado
    WIDGET_SELECTED = "WIDGET_SELECTED"               # Widget seleccionado
    WIDGET_DESELECTED = "WIDGET_DESELECTED"           # Widget deseleccionado
    STATE_SAVED = "STATE_SAVED"                       # Estado guardado
    STATE_LOADED = "STATE_LOADED"                     # Estado cargado
    PROJECT_OPENED = "PROJECT_OPENED"                 # Proyecto abierto
    PROJECT_CLOSED = "PROJECT_CLOSED"                 # Proyecto cerrado
    THEME_CHANGED = "THEME_CHANGED"                   # Tema cambiado