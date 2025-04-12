import customtkinter as ctk
import tkinter as tk


class ZoomableCanvas(ctk.CTkCanvas):
    """
    Canvas con soporte para zoom y panorámica, compatible con CustomTkinter.
    """
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        # Estados de zoom y panorámica
        self.zoom_level = 1.0
        self.pan_start = None

        # Configurar eventos
        self._bind_events()

    def _bind_events(self):
        """Configurar eventos para zoom y panorámica."""
        self.bind("<MouseWheel>", self._on_mousewheel)
        self.bind("<ButtonPress-2>", self._start_pan)
        self.bind("<B2-Motion>", self._pan)
        self.bind("<ButtonRelease-2>", self._end_pan)

    def _on_mousewheel(self, event):
        """Manejar eventos de zoom."""
        scale = 1.1 if event.delta > 0 else 0.9
        self._zoom(scale, event.x, event.y)

    def _start_pan(self, event):
        """Iniciar operación de panorámica."""
        self.config(cursor="fleur")
        self.pan_start = (event.x, event.y)

    def _pan(self, event):
        """Actualizar posición durante la panorámica."""
        if self.pan_start is not None:
            # Calcular el desplazamiento
            dx = event.x - self.pan_start[0]
            dy = event.y - self.pan_start[1]
            
            # Mover la vista del canvas
            self.xview_scroll(-dx, "units")
            self.yview_scroll(-dy, "units")
            
            # Actualizar posición inicial
            self.pan_start = (event.x, event.y)

    def _end_pan(self, event):
        """Finalizar operación de panorámica."""
        self.config(cursor="")
        self.pan_start = None

    def _zoom(self, scale, x, y):
        """Aplicar zoom centrado en un punto."""
        # Limitar el nivel de zoom
        new_zoom_level = self.zoom_level * scale
        if not (0.1 <= new_zoom_level <= 10):
            return

        # Calcular el punto de zoom en coordenadas del canvas
        canvas_x = self.canvasx(x)
        canvas_y = self.canvasy(y)

        # Escalar todos los elementos del canvas
        self.scale("all", canvas_x, canvas_y, scale, scale)
        
        # Actualizar nivel de zoom
        self.zoom_level = new_zoom_level
        
        # Actualizar región de desplazamiento
        self.configure(scrollregion=self.bbox("all"))

    def reset_view(self):
        """Restablecer el zoom y la panorámica."""
        # Restablecer nivel de zoom
        scale = 1.0 / self.zoom_level
        self.scale("all", 0, 0, scale, scale)
        self.zoom_level = 1.0
        
        # Restablecer vista
        self.configure(scrollregion=self.bbox("all"))
        self.xview_moveto(0)
        self.yview_moveto(0)


# Ejemplo de uso con CustomTkinter
if __name__ == "__main__": 
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Canvas con Zoom y Panorámica (CTk)")
    root.geometry("800x600")

    # Crear canvas
    canvas = ZoomableCanvas(root, bg="white")
    canvas.pack(fill=tk.BOTH, expand=True)

    # Añadir widgets de ejemplo
    for i in range(5):
        x, y = 100 + i * 120, 100
        btn = ctk.CTkButton(canvas, text=f"Botón {i+1}")
        canvas.create_window(x, y, window=btn)

    # Añadir líneas guía de ejemplo
    canvas.create_line(50, 50, 750, 50, fill="red", dash=(4, 2))
    canvas.create_line(50, 50, 50, 550, fill="red", dash=(4, 2))

    # Controles de zoom
    toolbar = ctk.CTkFrame(root)
    toolbar.pack(side=tk.TOP, fill=tk.X)
    ctk.CTkButton(toolbar, text="Zoom +", command=lambda: canvas._zoom(1.1, 400, 300)).pack(side=tk.LEFT, padx=5, pady=5)
    ctk.CTkButton(toolbar, text="Zoom -", command=lambda: canvas._zoom(0.9, 400, 300)).pack(side=tk.LEFT, padx=5, pady=5)
    ctk.CTkButton(toolbar, text="Reset", command=canvas.reset_view).pack(side=tk.LEFT, padx=5, pady=5)

    root.mainloop()