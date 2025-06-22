import logging
import json
from pathlib import Path
from plugins.plugin_manager import Plugin
import customtkinter as CTk
from tkinter import filedialog, messagebox
import re

class Plugin(Plugin):
    def __init__(self):
        self.name = "Export Format Manager" 
        self.version = "1.0.0"
        self.description = "Manage different code export formats"
        self.author = "InnoDev69"
        
        # Configuration file path
        self.config_path = Path("plugins/ExportFormatManager/formats.json")
        
        # Default format templates
        self.default_formats = {
            "customtkinter": {
                "name": "CustomTkinter (Default)",
                "imports": "import customtkinter as ctk\n",
                "class_def": "class App(ctk.CTk):",
                "init_method": """    def __init__(self):
        super().__init__()
        self.geometry('{window_width}x{window_height}')
        self.title('Exported Virtual Window')
        
        self.resizable({resizable},{resizable})
        self.virtual_window = ctk.CTkFrame(self, {window_params})
        self.virtual_window.pack(expand=True, fill='both')
        self.generic_widget_creator()""",
                "creator_method": "    def generic_widget_creator(self):",
                "widget_template": "        self.{widget_name} = ctk.{widget_type}(self.virtual_window, {widget_params})",
                "widget_placement": "        self.{widget_name}.place(x={x}, y={y})",
                "widget_no_name": "        ctk.{widget_type}(self.virtual_window, {widget_params}).place(x={x}, y={y})",
                "footer": """
if __name__ == '__main__':
    app = App()
    app.mainloop()""",
                "file_extension": ".py"
            },
            "tkinter": {
                "name": "Tkinter (Standard)",
                "imports": "import tkinter as tk\nfrom tkinter import ttk\n",
                "class_def": "class App(tk.Tk):",
                "init_method": """    def __init__(self):
        super().__init__()
        self.geometry('{window_width}x{window_height}')
        self.title('Exported Virtual Window')
        
        self.resizable({resizable_bool},{resizable_bool})
        self.virtual_window = tk.Frame(self, {window_params})
        self.virtual_window.pack(expand=True, fill='both')
        self.generic_widget_creator()""",
                "creator_method": "    def generic_widget_creator(self):",
                "widget_template": "        self.{widget_name} = tk.{widget_type}(self.virtual_window, {widget_params})",
                "widget_placement": "        self.{widget_name}.place(x={x}, y={y})",
                "widget_no_name": "        tk.{widget_type}(self.virtual_window, {widget_params}).place(x={x}, y={y})",
                "footer": """
if __name__ == '__main__':
    app = App()
    app.mainloop()""",
                "file_extension": ".py"
            },
            "pyside6": {
                "name": "PySide6 (Qt)",
                "imports": """from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtWidgets import QPushButton, QLabel, QLineEdit, QTextEdit
from PySide6.QtCore import Qt
import sys
""",
                "class_def": "class App(QMainWindow):",
                "init_method": """    def __init__(self):
        super().__init__()
        self.setWindowTitle('Exported Virtual Window')
        self.setGeometry(100, 100, {window_width}, {window_height})
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.setup_widgets()""",
                "creator_method": "    def setup_widgets(self):",
                "widget_template": "        self.{widget_name} = {qt_widget_type}(self.central_widget)",
                "widget_placement": "        self.{widget_name}.move({x}, {y})\n        self.{widget_name}.resize({width}, {height})",
                "widget_no_name": """        widget_{index} = {qt_widget_type}(self.central_widget)
        widget_{index}.move({x}, {y})
        widget_{index}.resize({width}, {height})""",
                "footer": """
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())""",
                "file_extension": ".py",
                "widget_mapping": {
                    "CTkButton": "QPushButton",
                    "CTkLabel": "QLabel", 
                    "CTkEntry": "QLineEdit",
                    "CTkTextbox": "QTextEdit",
                    "CTkFrame": "QWidget"
                }
            },
            "html": {
                "name": "HTML/CSS/JS",
                "imports": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exported Virtual Window</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }}
        .virtual-window {{
            width: {window_width}px;
            height: {window_height}px;
            position: relative;
            background-color: {bg_color};
            margin: 20px auto;
            border: 1px solid #ccc;
        }}
        .widget {{
            position: absolute;
        }}
    </style>
</head>
<body>""",
                "class_def": """    <div class="virtual-window">""",
                "init_method": "",
                "creator_method": "",
                "widget_template": """        <{html_tag} class="widget" style="left: {x}px; top: {y}px; {style}">{content}</{html_tag}>""",
                "widget_placement": "",
                "widget_no_name": """        <{html_tag} class="widget" style="left: {x}px; top: {y}px; {style}">{content}</{html_tag}>""",
                "footer": """    </div>
</body>
</html>""",
                "file_extension": ".html",
                "widget_mapping": {
                    "CTkButton": {"tag": "button", "content": "{text}"},
                    "CTkLabel": {"tag": "div", "content": "{text}"},
                    "CTkEntry": {"tag": "input", "content": "", "extra": 'type="text" value="{text}"'},
                    "CTkTextbox": {"tag": "textarea", "content": "{text}"},
                    "CTkFrame": {"tag": "div", "content": ""}
                }
            }
        }
        
        # Load formats from config
        self.formats = self.load_formats()
        
        # Current selected format
        self.current_format = "customtkinter"
        
    def load_formats(self):
        """Load formats from configuration file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    saved_formats = json.load(f)
                # Merge with defaults, prioritizing saved formats
                formats = self.default_formats.copy()
                formats.update(saved_formats)
                return formats
            else:
                self.save_formats()
                return self.default_formats.copy()
        except Exception as e:
            logging.error(f"Error loading formats: {e}")
            return self.default_formats.copy()
            
    def save_formats(self):
        """Save formats to configuration file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.formats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error saving formats: {e}")
        
    def on_initialize(self) -> None:
        """Initialize export format manager"""
        # Add to plugin menu
        self.app.plugin_button_drop.add_separator()
        self.app.plugin_button_drop.add_option(
            "Export Format Manager", 
            self.open_format_manager
        )
        
        # Add to main menu
        self.app.menu_button_drop.add_separator()
        export_submenu = self.app.menu_button_drop.add_submenu("Export Formats", 4)
        
        for format_key, format_data in self.formats.items():
            export_submenu.add_option(
                f"Export as {format_data['name']}", 
                lambda fk=format_key: self.export_with_format(fk)
            )
        
    def open_format_manager(self):
        """Open format manager window"""
        if hasattr(self, 'window') and self.window.winfo_exists():
            self.window.lift()
            return
            
        self.window = CTk.CTkToplevel(self.app)
        self.window.title("Export Format Manager")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        # Main container
        main_frame = CTk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Top frame for format selection and buttons
        top_frame = CTk.CTkFrame(main_frame)
        top_frame.pack(fill="x", pady=(0, 10))
        
        # Format selection
        CTk.CTkLabel(top_frame, text="Select Format:", font=("Arial", 14, "bold")).pack(side="left", padx=5)
        
        self.format_var = CTk.StringVar(value=self.current_format)
        self.format_dropdown = CTk.CTkOptionMenu(
            top_frame,
            variable=self.format_var,
            values=list(self.formats.keys()),
            command=self.on_format_change
        )
        self.format_dropdown.pack(side="left", padx=10)
        
        # Buttons
        button_frame = CTk.CTkFrame(top_frame)
        button_frame.pack(side="right", padx=5)
        
        CTk.CTkButton(
            button_frame,
            text="Export with Format",
            command=self.export_current_format,
            width=120
        ).pack(side="left", padx=2)
        
        CTk.CTkButton(
            button_frame,
            text="Preview",
            command=self.preview_export,
            width=80
        ).pack(side="left", padx=2)
        
        CTk.CTkButton(
            button_frame,
            text="Edit Format",
            command=self.edit_format,
            width=100
        ).pack(side="left", padx=2)
        
        # Preview area    
        preview_frame = CTk.CTkFrame(main_frame)
        preview_frame.pack(fill="both", expand=True)
        
        CTk.CTkLabel(preview_frame, text="Export Preview:", font=("Arial", 12, "bold")).pack(anchor="w", padx=5, pady=(5, 0))
        
        self.preview_text = CTk.CTkTextbox(preview_frame, font=("Courier", 10))
        self.preview_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Update preview
        self.update_preview()
        
    def on_format_change(self, format_key):
        """Handle format selection change"""
        self.current_format = format_key
        self.update_preview()
        
    def update_preview(self):
        """Update the preview text"""
        if not hasattr(self, 'preview_text'):
            return
            
        try:
            preview_code = self.generate_export_code(self.current_format)
            self.preview_text.delete('1.0', 'end')
            self.preview_text.insert('1.0', preview_code)
        except Exception as e:
            self.preview_text.delete('1.0', 'end')
            self.preview_text.insert('1.0', f"Error generating preview: {e}")
            
    def generate_export_code(self, format_key):
        """Generate export code for the specified format"""
        if format_key not in self.formats:
            raise ValueError(f"Unknown format: {format_key}")

        format_template = self.formats[format_key]

        # Get window properties
        window_width = self.app.virtual_window.winfo_width()
        window_height = self.app.virtual_window.winfo_height()
        window_params = self._get_window_params_string()
        resizable = bool(self.app.config_manager.get("Export", "resizable"))

        # Start building the code
        code_lines = []

        # Add imports
        imports = format_template.get("imports", "")
        if imports:
            code_lines.append(imports.format(
                window_width=window_width,
                window_height=window_height,
                bg_color=self.app.virtual_window.cget("fg_color")
            ))

        # Add class definition
        if format_template.get("class_def"):
            code_lines.extend(("", format_template["class_def"]))
        # Add init method
        if format_template.get("init_method"):
            code_lines.append(format_template["init_method"].format(
                window_width=window_width,
                window_height=window_height,
                window_params=window_params,
                resizable=str(resizable).lower(),
                resizable_bool="True" if resizable else "False"
            ))

        # Add creator method
        if format_template.get("creator_method"):
            code_lines.extend(("", format_template["creator_method"]))
        # Add widgets
        if self.app.virtual_window.widgets:
            widget_lines = self._generate_widget_code(format_template)
            code_lines.extend(widget_lines)

        elif format_key != "html":
            code_lines.append("        pass")
        # Add footer
        if format_template.get("footer"):
            code_lines.append(format_template["footer"])

        return "\n".join(code_lines)
        
    def _get_window_params_string(self):
        """Get window parameters as formatted string"""
        window_params = {
            "fg_color": self.app.virtual_window.cget("fg_color"),
            "bg_color": self.app.virtual_window.cget("bg_color"),
            "width": self.app.virtual_window.cget("width"),
            "height": self.app.virtual_window.cget("height"),
        }
        return ", ".join(f"{k}={repr(v)}" for k, v in window_params.items())
        
    def _generate_widget_code(self, format_template):
        """Generate widget code based on format template"""
        widget_lines = []
        font_pattern = re.compile(r"<customtkinter\.windows\.widgets\.font\.ctk_font\.CTkFont object 'font\d{1,3}'>")
        font_pattern_ = re.compile(r'font\d{1,3}')

        for i, widget in enumerate(self.app.virtual_window.widgets):
            widget_type = widget.__class__.__name__
            x, y = widget.winfo_x(), widget.winfo_y()
            width, height = widget.winfo_width(), widget.winfo_height()

            # Get widget parameters
            widget_params = self._get_widget_params(widget, font_pattern, font_pattern_)

            # Check if widget has a name
            widget_name = None
            if hasattr(self.app.virtual_window, 'left_sidebar') and widget._name in self.app.virtual_window.left_sidebar.widget_dict:
                widget_name = self.app.virtual_window.left_sidebar.widget_dict[widget._name]

            # Generate code based on format
            if format_template.get("widget_mapping") and widget_type in format_template["widget_mapping"]:
                # Handle special widget mappings (like Qt or HTML)
                mapped_widget = format_template["widget_mapping"][widget_type]

                if self.current_format == "html":
                    # HTML format
                    tag_info = mapped_widget
                    html_tag = tag_info["tag"]
                    content = tag_info.get("content", "").format(text=widget_params.get("text", ""))
                    extra = tag_info.get("extra", "")
                    style = f"width: {width}px; height: {height}px;"

                    widget_line = format_template["widget_template"].format(
                        html_tag=html_tag,
                        x=x,
                        y=y,
                        style=style + (f" {extra}" if extra else ""),
                        content=content,
                    )
                elif self.current_format == "pyside6":
                    # Qt format
                    if widget_name:
                        widget_line = format_template["widget_template"].format(
                            widget_name=widget_name,
                            qt_widget_type=mapped_widget
                        )
                        placement_line = format_template["widget_placement"].format(
                            widget_name=widget_name,
                            x=x, y=y, width=width, height=height
                        )
                        widget_lines.extend((widget_line, placement_line))
                        continue
                    else:
                        widget_line = format_template["widget_no_name"].format(
                            index=i,
                            qt_widget_type=mapped_widget,
                            x=x, y=y, width=width, height=height
                        )
            elif widget_name:
                widget_line = format_template["widget_template"].format(
                    widget_name=widget_name,
                    widget_type=widget_type,
                    widget_params=widget_params
                )
                placement_line = format_template.get("widget_placement", "").format(
                    widget_name=widget_name,
                    x=x, y=y
                )
                widget_lines.append(widget_line)
                if placement_line:
                    widget_lines.append(placement_line)
                continue
            else:
                widget_line = format_template["widget_no_name"].format(
                    widget_type=widget_type,
                    widget_params=widget_params,
                    x=x, y=y
                )

            widget_lines.append(widget_line)

        return widget_lines
        
    def _get_widget_params(self, widget, font_pattern, font_pattern_):
        """Get widget parameters as formatted string"""
        from data.variable import global_properties
        
        widget_params = {}
        widget_type = widget.__class__.__name__
        properties = global_properties.get(widget_type, [])
        
        for prop in properties:
            if prop in (None, "", "default"):
                continue
                
            try:
                param_value = widget.cget(prop)
                if prop.lower() == "font" and (
                    font_pattern.match(str(param_value)) or 
                    font_pattern_.match(str(param_value))
                ):
                    continue
                    
                widget_params[prop] = param_value
            except Exception:
                continue
        
        if self.current_format == "html":
            return widget_params
        else:
            return ", ".join(f"{k}={repr(v)}" for k, v in widget_params.items())
            
    def export_current_format(self):
        """Export using currently selected format"""
        self.export_with_format(self.current_format)
        
    def export_with_format(self, format_key):
        """Export the virtual window with specified format"""
        if format_key not in self.formats:
            messagebox.showerror("Error", f"Unknown format: {format_key}")
            return
            
        format_template = self.formats[format_key]
        file_extension = format_template.get("file_extension", ".txt")
        
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            title=f"Export as {format_template['name']}",
            defaultextension=file_extension,
            filetypes=[(f"{format_template['name']} files", f"*{file_extension}"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            # Generate code
            code = self.generate_export_code(format_key)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
                
            self.app.cross_update_text_info(f"Exported successfully as {format_template['name']}: {file_path}")
            messagebox.showinfo("Success", f"File exported successfully!\n{file_path}")
            
        except Exception as e:
            logging.error(f"Export error: {e}")
            messagebox.showerror("Export Error", f"Failed to export file:\n{e}")
            
    def preview_export(self):
        """Preview the export without saving"""
        self.update_preview()
        
    def edit_format(self):
        """Open format editor window"""
        editor_window = CTk.CTkToplevel(self.window)
        editor_window.title(f"Edit Format: {self.formats[self.current_format]['name']}")
        editor_window.geometry("600x500")
        
        # Format editing interface would go here
        # This would allow users to modify templates, add new formats, etc.
        CTk.CTkLabel(
            editor_window, 
            text="Format Editor\n(Advanced feature - would allow editing format templates)",
            font=("Arial", 14)
        ).pack(expand=True)
        
        CTk.CTkButton(
            editor_window,
            text="Close",
            command=editor_window.destroy
        ).pack(pady=10)
        
    def cleanup(self) -> None:
        """Cleanup when plugin is disabled"""
        self.save_formats()
        logging.info("Export Format Manager plugin cleaned up")