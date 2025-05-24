import json
import customtkinter as ctk
from typing import Dict, Any
import logging

class ThemeManager(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.current_theme = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        self.header = ctk.CTkLabel(self, text="Theme Manager", font=("Arial", 20, "bold"))
        self.header.pack(pady=10)
        
        # Theme properties frame
        self.props_frame = ctk.CTkScrollableFrame(self, width=400, height=500)
        self.props_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Theme sections
        self.sections = {
            "Window": self.create_window_section(),
            "Buttons": self.create_button_section(),
            "Labels": self.create_label_section(),
            "Entries": self.create_entry_section(),
            "Frames": self.create_frame_section()
        }
        
        # Actions frame
        self.actions_frame = ctk.CTkFrame(self)
        self.actions_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(self.actions_frame, text="Save Theme", command=self.save_theme).pack(side="left", padx=5)
        ctk.CTkButton(self.actions_frame, text="Load Theme", command=self.load_theme).pack(side="left", padx=5)
        ctk.CTkButton(self.actions_frame, text="Apply Theme", command=self.apply_theme).pack(side="left", padx=5)
        
    def create_color_picker(self, parent, label, default="#000000"):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(frame, text=label).pack(side="left", padx=5)
        
        color_btn = ctk.CTkButton(frame, text=default, width=100, 
                                fg_color=default,
                                command=lambda: self.pick_color(color_btn))
        color_btn.pack(side="right", padx=5)
        return color_btn
        
    def create_window_section(self):
        frame = self._extracted_from_create_frame_section_2("Window")
        return {
            "background": self.create_color_picker(frame, "Background", "#2b2b2b"),
            "foreground": self.create_color_picker(frame, "Foreground", "#ffffff"),
        }
        
    def create_button_section(self):
        frame = self._extracted_from_create_frame_section_2("Buttons")
        return {
            "fg_color": self.create_color_picker(frame, "Background", "#1f538d"),
            "text_color": self.create_color_picker(frame, "Text", "#ffffff"),
            "hover_color": self.create_color_picker(frame, "Hover", "#14375e"),
            "border_color": self.create_color_picker(frame, "Border", "#949A9F"),
        }

    def create_label_section(self):
        frame = self._extracted_from_create_frame_section_2("Labels")
        return {
            "fg_color": self.create_color_picker(
                frame, "Background", "transparent"
            ),
            "text_color": self.create_color_picker(frame, "Text", "#ffffff"),
            "border_color": self.create_color_picker(frame, "Border", "#949A9F"),
        }

    def create_entry_section(self):
        frame = self._extracted_from_create_frame_section_2("Entries")
        return {
            "fg_color": self.create_color_picker(frame, "Background", "#343638"),
            "text_color": self.create_color_picker(frame, "Text", "#ffffff"),
            "border_color": self.create_color_picker(frame, "Border", "#565B5E"),
            "placeholder_text_color": self.create_color_picker(
                frame, "Placeholder", "#6B7278"
            ),
        }

    def create_frame_section(self):
        frame = self._extracted_from_create_frame_section_2("Frames")
        return {
            "fg_color": self.create_color_picker(frame, "Background", "#2b2b2b"),
            "border_color": self.create_color_picker(frame, "Border", "#949A9F"),
        }

    # TODO Rename this here and in `create_window_section`, `create_button_section`, `create_label_section`, `create_entry_section` and `create_frame_section`
    def _extracted_from_create_frame_section_2(self, text):
        result = ctk.CTkFrame(self.props_frame)
        result.pack(fill="x", pady=10)
        ctk.CTkLabel(result, text=text, font=("Arial", 16, "bold")).pack()
        return result

    def pick_color(self, button):
        """Open color picker and update button color"""
        try:
            import tkinter.colorchooser as colorchooser
            color = colorchooser.askcolor(title="Choose color", color=button.cget("text"))
            if color[1]:  # color[1] contains the hex value
                button.configure(text=color[1], fg_color=color[1])
        except ImportError:
            logging.error("Could not import tkinter.colorchooser")
    
    def save_theme(self):
        theme = {
            section: {
                prop: picker.cget("text") for prop, picker in properties.items()
            }
            for section, properties in self.sections.items()
        }
        if filename := ctk.filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON files", "*.json")]
        ):
            with open(filename, "w") as f:
                json.dump(theme, f, indent=2)
            logging.info(f"Theme saved to {filename}")
            
    def load_theme(self):
        if not (
            filename := ctk.filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json")]
            )
        ):
            return
        with open(filename) as f:
            theme = json.load(f)

        for section, properties in theme.items():
            if section in self.sections:
                for prop, value in properties.items():
                    if prop in self.sections[section]:
                        self.sections[section][prop].configure(
                            text=value,
                            fg_color=value
                        )

        self.current_theme = theme
        logging.info(f"Theme loaded from {filename}")
            
    def apply_theme(self):
        if not self.current_theme:
            logging.warning("No theme loaded")
            return
            
        # Aplicar el tema a la VirtualWindow y sus widgets
        self.app.virtual_window.configure(
            fg_color=self.current_theme["Window"]["background"]
        )
        
        for widget in self.app.virtual_window.widgets:
            widget_type = widget.__class__.__name__
            if widget_type in self.current_theme:
                widget.configure(**self.current_theme[widget_type])
                
        logging.info("Theme applied successfully")