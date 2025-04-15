import customtkinter as ctk
import tkinter as tk
import math
import colorsys
from objects.tooltip import CTkToolTip as ToolTip

class ColorWheel(ctk.CTkFrame):
    def __init__(self, master, initial_color="#FF0000",command=None, size=200, **kwargs):
        super().__init__(master, **kwargs)
        self.size = size
        self.command = command
        self.current_color = initial_color
        self.hue = 0
        self.saturation = 1
        self.value = 1
        
        # Canvas para la rueda de colores
        self.canvas = tk.Canvas(self, width=size, height=size, 
                              bg=self.cget("fg_color")[1], highlightthickness=0)
        self.canvas.pack(padx=10, pady=10)
        
        # Barra de brillo
        self.brightness_frame = ctk.CTkFrame(self)
        self.brightness_frame.pack(fill="x", padx=10, pady=(0,10))
        
        self.brightness_label = ctk.CTkLabel(self.brightness_frame, text="Brillo:")
        self.brightness_label.pack(side="left", padx=5)
        
        self.brightness_slider = ctk.CTkSlider(
            self.brightness_frame,
            from_=0,
            to=1,
            number_of_steps=100,
            command=self._on_brightness_change
        )
        self.brightness_slider.set(1)  # Valor inicial
        self.brightness_slider.pack(side="right", fill="x", expand=True, padx=5)
        
        # Crear rueda de colores
        self.draw_color_wheel()
        
        # Marcador del color seleccionado
        self.selector = self.canvas.create_oval(0, 0, 10, 10, outline="white", width=2)
        self.update_selector()
        
        # Eventos de mouse
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)

    def _update_current_color(self, color):
        """Actualiza el color actual"""
        self.current_color = color
        print(self.current_color)
        self.update_selector()
        if self.command:
            self.command(self.current_color)

    def set_color(self, color_hex):
        """
        Actualiza la rueda de colores y el selector basado en un color hexadecimal
        
        Args:
            color_hex: Color en formato hexadecimal (ej: "#FF0000")
        """
        # Validar formato
        if not color_hex.startswith("#") or len(color_hex) != 7:
            print(f"Formato de color inválido: {color_hex}")
            return
        
        try:
            # Convertir de hexadecimal a RGB
            r = int(color_hex[1:3], 16) / 255.0
            g = int(color_hex[3:5], 16) / 255.0
            b = int(color_hex[5:7], 16) / 255.0
            
            # Convertir de RGB a HSV
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            
            # Actualizar los valores internos
            self.hue = h
            self.saturation = s
            self.value = v
            self.current_color = color_hex
            
            # Actualizar el slider de brillo
            self.brightness_slider.set(v)
            
            # Actualizar la posición visual del selector
            self.update_selector()
            
            # Llamar al callback si existe
            if self.command:
                self.command(self.current_color)
        
        except ValueError as e:
            print(f"Error al procesar el color: {e}")

    def _on_brightness_change(self, value):
        """Maneja cambios en el control de brillo"""
        self.value = float(value)
        self._update_current_color()
    
    def _update_current_color(self):
        """Actualiza el color actual basado en HSV"""
        r, g, b = colorsys.hsv_to_rgb(self.hue, self.saturation, self.value)
        self.current_color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        if self.command:
            self.command(self.current_color)
    
    def draw_color_wheel(self):
        """Dibuja la rueda de colores en el canvas"""
        center_x = self.size / 2
        center_y = self.size / 2
        radius = (self.size - 20) / 2
        
        # Dibujar la rueda de colores por segmentos
        for angle in range(0, 360, 1):
            # Convertir el ángulo a radianes
            rad = math.radians(angle)
            
            # Calcular los puntos del segmento
            x1 = center_x + (radius - 10) * math.cos(rad)
            y1 = center_y + (radius - 10) * math.sin(rad)
            x2 = center_x + radius * math.cos(rad)
            y2 = center_y + radius * math.sin(rad)
            
            # Convertir HSV a RGB
            hue = angle / 360.0
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            
            # Convertir RGB a hexadecimal
            color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
            
            # Dibujar el segmento
            self.canvas.create_line(x1, y1, x2, y2, width=20, fill=color)
        
        # Dibujar el círculo central para la saturación/valor
        self.canvas.create_oval(
            center_x - radius/3, center_y - radius/3,
            center_x + radius/3, center_y + radius/3,
            fill="white", outline="gray"
        )
    
    def update_selector(self):
        """Actualiza la posición del selector según el color actual"""
        center_x = self.size / 2
        center_y = self.size / 2
        radius = (self.size - 20) / 2 - 5
        
        # Calcular la posición basada en el tono (hue)
        angle_rad = 2 * math.pi * self.hue
        x = center_x + radius * math.cos(angle_rad)
        y = center_y + radius * math.sin(angle_rad)
        
        # Actualizar la posición del selector
        self.canvas.coords(self.selector, x-5, y-5, x+5, y+5)
    
    def on_click(self, event):
        """Maneja el evento de clic para seleccionar un color"""
        self.update_color(event.x, event.y)
    
    def on_drag(self, event):
        """Maneja el evento de arrastre para cambiar el color"""
        self.update_color(event.x, event.y)
    
    def update_color(self, x, y):
        center_x = self.size / 2
        center_y = self.size / 2
        
        dx = x - center_x
        dy = y - center_y
        distance = math.sqrt(dx**2 + dy**2)
        max_radius = (self.size - 20) / 2
        
        if distance > max_radius:
            return
        
        angle = math.atan2(dy, dx)
        if angle < 0:
            angle += 2 * math.pi
            
        self.hue = angle / (2 * math.pi)
        
        # Calcular saturación basada en la distancia al centro
        self.saturation = min(distance / max_radius, 1.0)
        
        # Actualizar color manteniendo el valor actual
        self._update_current_color()
        self.update_selector()

class ColorPickerApp(ctk.CTkFrame):
    def __init__(self, master=None, initial_color="#FF0000", **kwargs):
        super().__init__(master, **kwargs)
        
        # Crear el frame principal scrollable
        self.main_container = ctk.CTkScrollableFrame(
            self,
            width=400,
            height=600,
            fg_color="transparent"
        )
        self.main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Etiqueta de título
        self.title_label = ctk.CTkLabel(
            self.main_container, 
            text="Selector de Color", 
            font=("Helvetica", 24)
        )
        self.title_label.grid(row=0, column=0, pady=(20, 10))
        
        # Color Wheel
        self.color_wheel = ColorWheel(
            self.main_container, 
            command=self.update_color_preview, 
            size=300
        )
        self.color_wheel.grid(row=1, column=0, padx=20, pady=20)
        
        # Frame para la previsualización y detalles
        self.preview_frame = ctk.CTkFrame(self.main_container)
        self.preview_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_columnconfigure(1, weight=1)
        
        # Cuadro de previsualización
        self.color_preview = ctk.CTkFrame(
            self.preview_frame, 
            width=100, 
            height=50
        )
        self.color_preview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Valor hexadecimal
        self.hex_value = ctk.CTkEntry(self.preview_frame)
        self.hex_value.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.hex_value.insert(0, initial_color)
        self.tooltip_color_status=ToolTip(self.hex_value,"Color no valido")
        self.tooltip_color_status.hide()

        # Actualizar color con entry
        self.hex_value.bind("<KeyRelease>",lambda event: self.update_color_preview(self.hex_value.get()))
        self.color_wheel.bind("<KeyRelease>", lambda event: self.color_wheel.set_colorI(self.hex_value.get()))

        # Inicializar con color rojo
        self.selected_color = initial_color
        self.update_color_preview(initial_color)
        
        # Agregar controles RGB
        self.rgb_frame = ctk.CTkFrame(self.main_container)
        self.rgb_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Sliders RGB
        self.r_slider = self._create_rgb_slider(self.rgb_frame, "R", 0)
        self.g_slider = self._create_rgb_slider(self.rgb_frame, "G", 1)
        self.b_slider = self._create_rgb_slider(self.rgb_frame, "B", 2)
        
        self.hex_value.bind("<Return>", self._on_hex_change)
        
        # Botones de acción
        self.buttons_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.buttons_frame.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
    def _create_rgb_slider(self, parent, label, row):
        """Crea un slider RGB con su etiqueta"""
        lbl = ctk.CTkLabel(parent, text=label)
        lbl.grid(row=row, column=0, padx=5, pady=2)
        
        slider = ctk.CTkSlider(
            parent,
            from_=0,
            to=255,
            number_of_steps=255,
            command=lambda v: self._on_rgb_change()
        )
        slider.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
        return slider
        
    def _on_rgb_change(self):
        """Actualiza el color cuando cambian los sliders RGB"""
        r = int(self.r_slider.get())
        g = int(self.g_slider.get())
        b = int(self.b_slider.get())
        color = f"#{r:02x}{g:02x}{b:02x}"
        self.update_color_preview(color)
        
    def _on_hex_change(self, event):
        """Valida y actualiza el color cuando cambia el valor hex"""
        color = self.hex_value.get()
        if len(color) == 7 and color.startswith("#"):
            try:
                # Validar formato hex
                int(color[1:], 16)
                self.update_color_preview(color)
            except ValueError:
                pass
    
    def update_color_preview(self, color):
        """Actualiza la previsualización del color y el valor hexadecimal"""
        try:
            #if self.tooltip_color_status.is_disabled:
            self.tooltip_color_status.hide()
            self.selected_color = color
            self.color_preview.configure(fg_color=color)
            self.hex_value.delete(0, tk.END)
            self.hex_value.insert(0, color)
            self.hex_value.configure(border_color="#5A5A5A")
        except tk.TclError:
            self.tooltip_color_status.show()
            self.hex_value.configure(border_color="red")
    
    def on_accept(self):
        """Devuelve el color seleccionado y cierra la aplicación"""
        print(f"Color seleccionado: {self.selected_color}")
        self.destroy()
        return self.selected_color
    
    def get_selected_color(self):
        """Método para obtener el color seleccionado"""
        return self.selected_color

def pick_color():
    """Función para mostrar el selector de color y devolver el color seleccionado"""
    app = ColorPickerApp()
    app.resizable(False, False)
    app.mainloop()
    return app.get_selected_color()

if __name__ == "__main__":
    selected_color = pick_color()
    print(f"Color devuelto: {selected_color}")