import logging
from pathlib import Path
from plugins.plugin_manager import Plugin
import customtkinter as CTk

class Plugin(Plugin):
    def __init__(self):
        self.name = "Export Format Manager" 
        self.version = "1.0.0"
        self.description = "Manage different code export formats"
        self.author = "InnoDev69"
        
        # Default format templates
        self.formats = {
            "basic": {
                "imports": "import customtkinter as ctk\n",
                "class_def": "class {name}(ctk.CTk):\n",
                "init": "    def __init__(self):\n        super().__init__()\n",
                "widget_template": "        self.{name} = ctk.{widget_type}({params})\n"
            },
            "pyside6": {
                "imports": "from PySide6.QtWidgets import *\n",
                "class_def": "class {name}(QMainWindow):\n",
                "init": "    def __init__(self):\n        super().__init__()\n",
                "widget_template": "        self.{name} = {widget_type}({params})\n"
            }
        }
        
    def on_initialize(self) -> None:
        """Initialize export format manager"""
        self.app.plugin_button_drop.add_separator()
        self.app.plugin_button_drop.add_option(
            "Export Formats", 
            self.open_format_manager
        )
        
    def open_format_manager(self):
        """Open format manager window"""
        self.window = CTk.CTkToplevel(self.app)
        self.window.title("Export Format Manager")
        self.window.geometry("600x400")
        
        # Format selection
        formats_frame = CTk.CTkFrame(self.window)
        formats_frame.pack(fill="x", padx=10, pady=5)
        
        CTk.CTkLabel(
            formats_frame, 
            text="Select Format:"
        ).pack(side="left", padx=5)
        
        self.format_var = CTk.StringVar(value="basic")
        
        for format_name in self.formats:
            CTk.CTkRadioButton(
                formats_frame,
                text=format_name,
                variable=self.format_var,
                value=format_name,
                command=self.update_preview
            ).pack(side="left", padx=10)
            
        # Preview area    
        preview_frame = CTk.CTkFrame(self.window)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.preview_text = CTk.CTkTextbox(preview_frame)
        self.preview_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.update_preview()