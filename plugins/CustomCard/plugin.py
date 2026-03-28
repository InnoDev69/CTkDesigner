from plugins.plugin_manager import Plugin

class Plugin(Plugin):
    def __init__(self):
        super().__init__()
        self.name = "Custom Card Widget"
        self.version = "1.0.0"
        self.description = "Agrega widget personalizado Card"
        self.author = "Dev"
    
    def initialize(self, app, retries=100, delay=5000):
        """Inicializar sin esperar a toolbar."""
        self.app = app
        
        try:
            from plugins.CustomCard.card_widget import CTkCardWidget
            import data.variable as var_module
            
            # Registrar en widget_classes
            var_module.widget_classes["CTkCardWidget"] = CTkCardWidget
            
            # Registrar propiedades
            var_module.global_properties["CTkCardWidget"] = [
                "title", "content", "fg_color", "width", "height",
                "border_width", "border_color", "corner_radius"
            ]
            
            # Agregar a lista de widgets (sincronizado con widgets_info)
            if "CTkCardWidget" not in var_module.widgets:
                var_module.widgets.append("CTkCardWidget")
                
                # IMPORTANTE: Agregar información en widgets_info para ambas lenguas
                if "es" in var_module.widgets_info:
                    var_module.widgets_info["es"].append("Una tarjeta personalizada para mostrar información con título y contenido.")
                
                if "en" in var_module.widgets_info:
                    var_module.widgets_info["en"].append("A custom card widget to display information with title and content.")
            
            self.logger.info(f"Plugin '{self.name}' initialized - CTkCardWidget registered")
            self.logger.info(f"  Total widgets: {len(var_module.widgets)}")
            
        except Exception as e:
            self.logger.error(f"Error initializing plugin: {e}")
            import traceback
            traceback.print_exc()