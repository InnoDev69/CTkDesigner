import tkinter as tk
import customtkinter as ctk
from typing import Dict, List, Callable, Optional, Tuple, Union
import sys

class CTkMenuBar(tk.Toplevel):
    def __init__(
        self, 
        master: any,
        bg_color: Optional[Union[str, Tuple[str, str]]] = "#2b2b2b",
        height: int = 25,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        # Configuración de la ventana del menú
        self.overrideredirect(True)
        self.attributes('-topmost', False)  # Cambiar a False por defecto
        self.transient(master)  # Hacer la ventana transitoria del master
        
        # Frame principal del menú
        self.menu_frame = ctk.CTkFrame(self, fg_color=bg_color, height=height)
        self.menu_frame.pack(fill="x")
        
        self.menus = {}
        self.buttons = {}
        self.active_menu = None
        self.is_menu_active = False
        
        # Vincular eventos
        self.bind('<Map>', self._on_map)
        self.master.bind('<Configure>', self._on_parent_configure)
        self.master.bind("<Button-1>", self._hide_active_menu)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Enter>', self._on_enter)
        
    def _on_enter(self, event=None):
        """Cuando el ratón entra al menú"""
        if self.active_menu:
            self.attributes('-topmost', True)
    
    def _on_leave(self, event=None):
        """Cuando el ratón sale del menú"""
        if not self.active_menu:
            self.attributes('-topmost', False)
    
    def _on_map(self, event=None):
        self._update_position()
        
    def _on_parent_configure(self, event=None):
        if event.widget == self.master:
            self._update_position()
    
    def _update_position(self):
        """Actualiza la posición del menú"""
        if not self.master.winfo_viewable():
            return
            
        x = self.master.winfo_x()
        y = self.master.winfo_y()
        width = self.master.winfo_width()
        
        # Ajuste para Windows
        if sys.platform == 'win32':
            y += 31
            
        self.geometry(f"{width}x{self.menu_frame.winfo_reqheight()}+{x}+{y}")
        
    def add_menu(self, name: str, options: List[Dict[str, Union[str, Callable]]], **kwargs):
        """Añade un menú a la barra"""
        button = ctk.CTkButton(
            self.menu_frame,
            text=name,
            fg_color="transparent",
            height=20,
            width=len(name)*8 + 10,
            **kwargs
        )
        button.pack(side="left", padx=2)
        self.buttons[name] = button
        
        menu = CTkMenu(
            self.master,
            options=options,
            **kwargs
        )
        self.menus[name] = menu
        
        button.configure(command=lambda n=name: self._show_menu(n))
        
    def _show_menu(self, name: str) -> None:
        """Muestra el menú desplegable."""
        if self.active_menu:
            self.menus[self.active_menu].hide()
            if self.active_menu == name:
                self.active_menu = None
                self.attributes('-topmost', False)
                return
        
        button = self.buttons[name]
        menu = self.menus[name]
        x = button.winfo_rootx()
        y = button.winfo_rooty() + button.winfo_height()
        menu.show(x, y)
        self.active_menu = name
        self.attributes('-topmost', True)
        
    def _hide_active_menu(self, event=None) -> None:
        """Oculta el menú activo cuando se hace clic fuera."""
        if self.active_menu:
            menu = self.menus[self.active_menu]
            if not menu.is_point_inside(event.x_root, event.y_root):
                menu.hide()
                self.active_menu = None
                self.attributes('-topmost', False)


class CTkMenu(ctk.CTkFrame):
    """
    Menú desplegable personalizado para CTkMenuBar.
    """
    def __init__(
        self, 
        master: any, 
        options: List[Dict[str, Union[str, Callable]]],
        width: int = 150,
        bg_color: Optional[Union[str, Tuple[str, str]]] = "transparent",  # Changed from None to "transparent"
        hover_color: Optional[Union[str, Tuple[str, str]]] = None,
        text_color: Optional[Union[str, Tuple[str, str]]] = None,
        font: Optional[tuple] = None,
        **kwargs
    ):
        super().__init__(
            master, 
            width=width,
            fg_color=bg_color,  # Changed bg_color to fg_color
            **kwargs
        )
        
        self.master = master
        self.options = options
        self.hover_color = hover_color or ("gray75", "gray25")
        self.text_color = text_color
        self.font = font
        self.width = width
        self.buttons = []
        
        # Crear botones para cada opción
        for option in options:
            if option.get("separator", False):
                separator = ctk.CTkFrame(
                    self, 
                    height=1, 
                    width=width-10,
                    fg_color=self.text_color
                )
                separator.pack(pady=2, padx=5)
            else:
                btn = ctk.CTkButton(
                    self,
                    text=option.get("label", ""),
                    command=option.get("command", None),
                    font=self.font,
                    text_color=self.text_color,
                    fg_color="transparent",
                    hover_color=self.hover_color,
                    anchor="w",
                    width=width-10,
                    height=30,
                )
                btn.pack(fill="x", padx=5, pady=2)
                self.buttons.append(btn)
        
        # Configurar el menú como oculto inicialmente
        self.withdraw()
        
    def show(self, x: int, y: int) -> None:
        """Muestra el menú en las coordenadas especificadas."""
        self.place(x=x, y=y)
        self.lift()
        self.focus_set()
        
    def hide(self) -> None:
        """Oculta el menú."""
        self.place_forget()
        
    def withdraw(self) -> None:
        """Oculta el menú."""
        self.place_forget()
        
    def is_point_inside(self, x: int, y: int) -> bool:
        """Verifica si un punto está dentro del menú."""
        if not self.winfo_viewable():
            return False
        
        widget_x = self.winfo_rootx()
        widget_y = self.winfo_rooty()
        widget_width = self.winfo_width()
        widget_height = self.winfo_height()
        
        return (widget_x <= x <= widget_x + widget_width and 
                widget_y <= y <= widget_y + widget_height)