import customtkinter as ctk
import tkinter as tk
import logging

class ZoomableCanvas(ctk.CTkCanvas):
    """
    Canvas con soporte para zoom y panorámica, compatible con CustomTkinter.
    Soporta widgets anidados y zoom uniforme.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zoom_level = 1.0
        self.pan_start = None
        self.widget_scales = {}  # Almacena las escalas originales de los widgets
        self._default_scaling = ctk.ScalingTracker.get_window_scaling(self.master)
        self.widgets_on_canvas = []  # Lista de widgets en el canvas
        
        # Configurar logging
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger('ZoomableCanvas')
        
        # Debug flags
        self.debug_mode = True
        self.highlight_scaled_widgets = True

        # Configurar eventos
        self._bind_events()
        self.logger.info("ZoomableCanvas initialized")

    def _bind_events(self):
        """Configurar eventos para zoom y panorámica."""
        # Zoom con rueda del ratón
        self.bind("<MouseWheel>", self._on_mousewheel)  # Windows
        self.bind("<Button-4>", self._on_mousewheel)    # Linux
        self.bind("<Button-5>", self._on_mousewheel)    # Linux
        
        # Pan con botón central del ratón
        self.bind("<ButtonPress-2>", self._start_pan)
        self.bind("<B2-Motion>", self._pan)
        
        # Doble clic con botón central para resetear
        self.bind("<Double-Button-2>", self._reset_view)

    def _on_mousewheel(self, event):
        """Manejar eventos de zoom."""
        # Obtener la posición del ratón relativa al canvas
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)

        # Determinar la dirección del zoom
        scale = 0.9 if event.num == 5 or event.delta < 0 else 1.1
        # Aplicar zoom
        self._zoom(scale, x, y)

    def _start_pan(self, event):
        """Iniciar operación de panorámica."""
        self.config(cursor="fleur")
        self.pan_start = (event.x, event.y)

    def _pan(self, event):
        """Actualizar posición durante la panorámica."""
        if not hasattr(self, 'pan_start'):
            return
            
        dx = event.x - self.pan_start[0]
        dy = event.y - self.pan_start[1]
        
        self.scan_dragto(event.x, event.y, gain=1)
        self.scan_mark(event.x, event.y)
        
        self.pan_start = (event.x, event.y)

    def _reset_view(self, event=None):
        """Restablecer el zoom y la panorámica."""
        # Resetear zoom y posición
        scale = 1.0 / self.zoom_level
        self._zoom(scale, self.winfo_width()/2, self.winfo_height()/2)
        self.zoom_level = 1.0
        
        # Centrar la vista
        self.xview_moveto(0)
        self.yview_moveto(0)

    def create_window(self, x, y, window=None, **kwargs):
        """Crear una ventana en el canvas y registrar el widget."""
        if window is not None:
            # Registrar el widget y sus dimensiones originales
            if isinstance(window, (ctk.CTkBaseClass, tk.Widget)):
                self._register_widget_with_children(window)
                self.widgets_on_canvas.append(window)
                
        return super().create_window(x, y, window=window, **kwargs)
    
    def _register_widget_with_children(self, widget):
        """Registra un widget y sus hijos recursivamente."""
        if isinstance(widget, ctk.CTkBaseClass):
            # Guardar dimensiones y escalado originales
            self.widget_scales[widget] = {
                "width": widget.cget("width") if widget.cget("width") is not None else 0,
                "height": widget.cget("height") if widget.cget("height") is not None else 0,
                "scaling": self._default_scaling
            }

            # Buscar widgets hijos en CustomTkinter
            if hasattr(widget, "winfo_children"):
                for child in widget.winfo_children():
                    self._register_widget_with_children(child)

    def update_all_widget_scales(self):
        """Actualiza las escalas de todos los widgets registrados según el zoom actual."""
        for widget in list(self.widget_scales.keys()):
            self._update_widget_scale(widget, self.zoom_level)
    
    def _update_widget_scale(self, widget, zoom_level):
        """Actualiza la escala de un widget específico y sus hijos."""
        if not widget.winfo_exists():
            # Si el widget ya no existe, eliminarlo del registro
            if widget in self.widget_scales:
                del self.widget_scales[widget]
            return

        if widget in self.widget_scales:
            self._extracted_from__update_widget_scale_10(widget, zoom_level)

    # TODO Rename this here and in `_update_widget_scale`
    def _extracted_from__update_widget_scale_10(self, widget, zoom_level):
        original = self.widget_scales[widget]

        # Ajustar tamaño si el widget tiene dimensiones definidas
        if original["width"] > 0:
            new_width = original["width"] * zoom_level
            widget.configure(width=new_width)

        if original["height"] > 0:
            new_height = original["height"] * zoom_level
            widget.configure(height=new_height)

        # Actualizar escalado para CustomTkinter
        new_scaling = original["scaling"] * zoom_level
        widget._set_scaling(new_widget_scaling=new_scaling, new_window_scaling=new_scaling)

        # Procesar widgets hijos (si existen)
        if hasattr(widget, "winfo_children"):
            for child in widget.winfo_children():
                self._update_widget_scale(child, zoom_level)

    def _zoom(self, scale, x, y):
        """Aplicar zoom centrado en un punto."""
        if self.debug_mode:
            self.logger.debug(f"Applying zoom: scale={scale}, x={x}, y={y}")
            self.logger.debug(f"Current zoom level: {self.zoom_level}")

        new_zoom_level = self.zoom_level * scale
        if not (0.1 <= new_zoom_level <= 10):
            self.logger.warning(f"Zoom level {new_zoom_level} out of bounds (0.1-10)")
            return

        # Calcular el desplazamiento para centrar el zoom en el cursor
        canvas_x = self.canvasx(x)
        canvas_y = self.canvasy(y)

        # Escalar todos los elementos del canvas
        self.scale("all", canvas_x, canvas_y, scale, scale)

        # Actualizar el nivel de zoom
        self.zoom_level = new_zoom_level

        # Debug info para widgets escalados
        windows = self.find_withtag("window")
        self.logger.debug(f"Found {len(windows)} windows to scale")

        for window_id in windows:
            if widget := self.itemcget(window_id, "window"):
                self._debug_print_widget_info(widget, "Scaling")
                if coords := self.coords(window_id):
                    self._scale_widget_tree(widget, scale)
                    if self.highlight_scaled_widgets:
                        self._highlight_widget(widget)

        # Actualizar todos los widgets y sus hijos
        self.update_all_widget_scales()

        # Actualizar la región de desplazamiento
        self.configure(scrollregion=self.bbox("all"))
        
        if self.debug_mode:
            self.logger.debug(f"New zoom level: {self.zoom_level}")

    def _scale_widget_tree(self, widget, scale):
        """Escala recursivamente un widget y todos sus widgets hijos"""
        if self.debug_mode:
            self._debug_print_widget_info(widget, "Before scaling")
        
        # Obtener las dimensiones actuales
        print(f"Escalando widget: {widget} con escala: {scale}")
        current_width = widget.winfo_width()
        current_height = widget.winfo_height()
        
        # Calcular las nuevas dimensiones
        new_width = int(current_width * scale)
        new_height = int(current_height * scale)
        
        # Aplicar las nuevas dimensiones
        widget.configure(width=new_width, height=new_height)
        
        if self.debug_mode:
            self._debug_print_widget_info(widget, "After scaling")
        
        # Escalar la fuente si el widget la tiene
        if hasattr(widget, 'cget') and 'font' in widget.keys():
            current_font = widget.cget('font')
            if hasattr(current_font, 'configure'):
                current_size = current_font.cget('size')
                new_size = int(current_size * scale)
                current_font.configure(size=new_size)
                if self.debug_mode:
                    self.logger.debug(f"Font scaled from {current_size} to {new_size}")
        
        # Recursivamente escalar todos los widgets hijos
        for child in widget.winfo_children():
            self._scale_widget_tree(child, scale)

    def reset_view(self):
        """Restablecer el zoom y la panorámica."""
        # Calcular la escala necesaria para volver al zoom 1.0
        reset_scale = 1.0 / self.zoom_level
        
        # Aplicar escala inversa a todos los elementos
        self.scale("all", 0, 0, reset_scale, reset_scale)
        self.zoom_level = 1.0
        
        # Restaurar todos los widgets a su escala original
        for widget in list(self.widget_scales.keys()):
            if widget.winfo_exists():
                original = self.widget_scales[widget]
                
                # Restaurar dimensiones
                if original["width"] > 0:
                    widget.configure(width=original["width"])
                
                if original["height"] > 0:
                    widget.configure(height=original["height"])
                
                # Restaurar escalado
                widget._set_scaling(
                    new_widget_scaling=original["scaling"],
                    new_window_scaling=original["scaling"]
                )
        
        # Actualizar la región de desplazamiento y resetear la vista
        self.configure(scrollregion=self.bbox("all"))
        self.xview_moveto(0)
        self.yview_moveto(0)
        
        # Forzar actualización
        self.update_idletasks()

    def _debug_print_widget_info(self, widget, action=""):
        """Imprime información detallada sobre un widget."""
        if self.debug_mode:
            self.logger.debug(f"""
            {action} Widget: {widget}
            - Type: {type(widget)}
            - Dimensions: {widget.winfo_width()}x{widget.winfo_height()}
            - Position: ({widget.winfo_x()}, {widget.winfo_y()})
            - Scaling: {self.widget_scales.get(widget, 'Not registered')}
            - Children count: {len(widget.winfo_children())}
            """)

    def _highlight_widget(self, widget, duration=500):
        """Resalta temporalmente un widget para debugging."""
        if self.highlight_scaled_widgets and hasattr(widget, 'configure'):
            original_bg = widget.cget('bg') if 'bg' in widget.keys() else None
            widget.configure(bg='yellow')
            self.after(duration, lambda: widget.configure(bg=original_bg))

    def toggle_debug_mode(self):
        """Activa/desactiva el modo debug."""
        self.debug_mode = not self.debug_mode
        self.logger.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)
        self.logger.info(f"Debug mode: {'ON' if self.debug_mode else 'OFF'}")

    def print_widget_hierarchy(self, widget=None, level=0):
        """Imprime la jerarquía completa de widgets."""
        if widget is None:
            widget = self
        
        indent = "  " * level
        self.logger.debug(f"{indent}Widget: {widget}")
        self.logger.debug(f"{indent}|- Type: {type(widget)}")
        self.logger.debug(f"{indent}|- Dimensions: {widget.winfo_width()}x{widget.winfo_height()}")
        
        for child in widget.winfo_children():
            self.print_widget_hierarchy(child, level + 1)

# Ejemplo de uso con CustomTkinter
if __name__ == "__main__": 
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Canvas con Zoom y Panorámica Mejorado (CTk)")
    root.geometry("800x600")

    # Crear canvas
    canvas = ZoomableCanvas(root, bg="white")
    canvas.pack(fill=tk.BOTH, expand=True)

    # Añadir widgets de ejemplo, incluyendo widgets anidados
    for i in range(3):
        x, y = 100 + i * 150, 100
        
        # Crear un frame que contendrá widgets anidados
        frame = ctk.CTkFrame(canvas, width=140, height=120)
        
        # Añadir widgets dentro del frame (anidados)
        label = ctk.CTkLabel(frame, text=f"Grupo {i+1}")
        label.pack(pady=5)
        
        btn1 = ctk.CTkButton(frame, text=f"Botón {i}.1", width=100)
        btn1.pack(pady=5)
        
        btn2 = ctk.CTkButton(frame, text=f"Botón {i}.2", width=100)
        btn2.pack(pady=5)
        
        # Colocar el frame en el canvas
        canvas.create_window(x, y, window=frame, anchor=tk.NW)
    
    # Añadir widgets individuales
    for i in range(2):
        x, y = 200 + i * 200, 300
        btn = ctk.CTkButton(canvas, text=f"Botón individual {i+1}")
        canvas.create_window(x, y, window=btn)

    # Añadir líneas guía de ejemplo
    canvas.create_line(50, 50, 750, 50, fill="red", dash=(4, 2))
    canvas.create_line(50, 50, 50, 550, fill="red", dash=(4, 2))

    # Controles de zoom
    toolbar = ctk.CTkFrame(root)
    toolbar.pack(side=tk.TOP, fill=tk.X)
    
    # Botones para controlar el zoom
    ctk.CTkButton(toolbar, text="Zoom +", command=lambda: canvas._zoom(1.1, 400, 300)).pack(side=tk.LEFT, padx=5, pady=5)
    ctk.CTkButton(toolbar, text="Zoom -", command=lambda: canvas._zoom(0.9, 400, 300)).pack(side=tk.LEFT, padx=5, pady=5)
    ctk.CTkButton(toolbar, text="Reset", command=canvas.reset_view).pack(side=tk.LEFT, padx=5, pady=5)
    
    # Botón para forzar actualización de todos los widgets
    ctk.CTkButton(toolbar, text="Actualizar Escalas", 
                 command=canvas.update_all_widget_scales).pack(side=tk.LEFT, padx=5, pady=5)

    root.mainloop()