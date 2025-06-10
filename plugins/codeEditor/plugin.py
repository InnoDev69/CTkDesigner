import customtkinter as ctk
from plugins.plugin_manager import Plugin
from objects.code_box import CTkCodeBox
from objects.CTkMenuBar.dropdown_menu import CustomDropdownMenu
import tkinter as tk
from CTkMessagebox import CTkMessagebox
import tempfile
import subprocess
import sys
import os

class Plugin(Plugin):
    def __init__(self):
        self.name = "Code Editor Plugin"
        self.version = "1.0.0"
        self.description = "Editor de código integrado para la VirtualWindow"
        self.author = "InnoDev69"

    def on_initialize(self) -> None:
        """Inicializa el plugin y agrega opciones al menú"""
        print("Inicializando Code Editor Plugin")
        self.app.plugin_button_drop.add_separator()
        self.app.plugin_button_drop.add_option("Abrir Editor de Código", self.view_code)

    def view_code(self):
        """Toggle between design view and code view."""
        if self.app.virtual_window.toggle_visibility():
            self._enter_code_view()
        else:
            self._exit_code_view()

    def _enter_code_view(self):
        """Enter code editing mode."""
        self.app.virtual_window.replace()
        self._create_code_editor()
        self.app.right_sidebar.disable_buttons()
        self._create_spinnets()
        
    def _create_spinnets(self):
        self.plugin_button_drop = CustomDropdownMenu(
            widget=self.app.menu_bar.add_cascade(text="Debugging"),
            master=self.app,
            width=150,
            fg_color="#2b2b2b",
            hover_color="#1f1f1f",
            corner_radius=8,
            border_width=1,
            border_color="grey30"
        )
        self.app.plugin_button_drop.change_option_text("Abrir Editor de Código", "Volver al Diseño")
        self.plugin_button_drop.add_option("Ejecutar Código", self._run_preview)
        
    def _delete_spinnets(self):
        """Delete the spinnets created for the code editor."""
        self.app.menu_bar.remove_button("Debugging")
    
    def _create_code_editor(self):
        """Create the code editor component."""
        self.code = CTkCodeBox(
            self.app.central_canvas, 
            height=500, 
            width=800, 
            language='python'
        )
        self.code.place(x=50, y=50)
        
        code_content = "\n".join(self.app.virtual_window.previsualize_code())
        self.code.insert('1.0', code_content)
        self.code.bind("<KeyRelease>", self.update_virtual_window)

    def _exit_code_view(self):
        """Exit code editing mode."""
        self.app.right_sidebar.enable_buttons()
        self.app.plugin_button_drop.change_option_text("Volver al Diseño", "Abrir Editor de Código")
        self._delete_spinnets()
        if hasattr(self, 'code'):
            self.code.destroy()
            
    def _run_preview(self):
        """Run the code preview in a separate process."""
        code_content = self.code.get('1.0', 'end-1c')
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file.write(code_content.encode('utf-8'))
            temp_file_path = temp_file.name
        
        try:
            subprocess.run([sys.executable, temp_file_path], check=True)
        except subprocess.CalledProcessError as e:
            CTkMessagebox(
                title="Error",
                message=f"Error al ejecutar el código: {e}",
                icon="cancel"
            )
        finally:
            os.remove(temp_file_path)

    def update_virtual_window(self, event):
        """Update virtual window with current code content."""
        new_code = self.code.get('1.0', 'end-1c')
        self.app.virtual_window.import_from_codebox(new_code)