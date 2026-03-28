import logging
import json
from pathlib import Path
from plugins.plugin_manager import Plugin
import customtkinter as CTk
from tkinter import filedialog, messagebox
import re
import ast
import sys
from datetime import datetime
from core.events import AppEvents

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False
    
try:
    import black
    BLACK_AVAILABLE = True
except ImportError:
    BLACK_AVAILABLE = False

class Plugin(Plugin):
    def __init__(self):
        super().__init__()
        self.name = "Export Format Manager" 
        self.version = "2.0.0"
        self.description = "Manage different code export formats with validation and formatting"
        self.author = "InnoDev69"
        
        # Configuration file path
        self.config_path = Path("plugins/ExportFormatManager/formats.json")
        self.history_path = Path("plugins/ExportFormatManager/export_history.json")
        
        # Export history tracking
        self.export_history = self.load_history()
        
        # Enhanced widget mapping with more types
        self.widget_mapping_extended = {
            "customtkinter": {
                "CTkButton": "CTkButton",
                "CTkLabel": "CTkLabel",
                "CTkEntry": "CTkEntry",
                "CTkTextbox": "CTkTextbox",
                "CTkFrame": "CTkFrame",
                "CTkCheckbox": "CTkCheckbox",
                "CTkSwitch": "CTkSwitch",
                "CTkSlider": "CTkSlider",
                "CTkProgressBar": "CTkProgressBar",
                "CTkComboBox": "CTkComboBox",
                "CTkOptionMenu": "CTkOptionMenu",
                "CTkSegmentedButton": "CTkSegmentedButton",
                "CTkTabview": "CTkTabview",
                "CTkScrollableFrame": "CTkScrollableFrame",
            },
            "tkinter": {
                "CTkButton": "tk.Button",
                "CTkLabel": "tk.Label",
                "CTkEntry": "tk.Entry",
                "CTkTextbox": "tk.Text",
                "CTkFrame": "tk.Frame",
                "CTkCheckbox": "tk.Checkbutton",
                "CTkSwitch": "tk.Scale",
                "CTkSlider": "tk.Scale",
                "CTkProgressBar": "ttk.Progressbar",
                "CTkComboBox": "ttk.Combobox",
                "CTkOptionMenu": "tk.OptionMenu",
                "CTkSegmentedButton": "tk.Frame",
                "CTkTabview": "ttk.Notebook",
                "CTkScrollableFrame": "tk.Frame",
            },
            "pyside6": {
                "CTkButton": "QPushButton",
                "CTkLabel": "QLabel",
                "CTkEntry": "QLineEdit",
                "CTkTextbox": "QTextEdit",
                "CTkFrame": "QWidget",
                "CTkCheckbox": "QCheckBox",
                "CTkSwitch": "QCheckBox",
                "CTkSlider": "QSlider",
                "CTkProgressBar": "QProgressBar",
                "CTkComboBox": "QComboBox",
                "CTkOptionMenu": "QPushButton",
                "CTkSegmentedButton": "QButtonGroup",
                "CTkTabview": "QTabWidget",
                "CTkScrollableFrame": "QScrollArea",
            }
        }
        
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
        
        # Initialize GUI
        self.setup_widgets()
        
    def setup_widgets(self):
        \"\"\"Setup all widgets for the application\"\"\"
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
        
    def load_history(self):
        """Load export history from file"""
        try:
            if self.history_path.exists():
                with open(self.history_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logging.error(f"Error loading history: {e}")
            return []
    
    def save_history(self):
        """Save export history to file"""
        try:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_path, 'w', encoding='utf-8') as f:
                json.dump(self.export_history[-50:], f, indent=2)  # Keep last 50 exports
        except Exception as e:
            logging.error(f"Error saving history: {e}")
    
    def add_to_history(self, format_key, file_path, status="success"):
        """Add export record to history"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "format": format_key,
            "file_path": str(file_path),
            "status": status
        }
        self.export_history.append(record)
        self.save_history()
    
    def validate_python_code(self, code):
        """Validate Python code syntax using ast.parse"""
        try:
            ast.parse(code)
            return True, "Syntax is valid!"
        except SyntaxError as e:
            return False, f"Syntax Error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def format_code(self, code):
        """Format code using black if available, otherwise basic formatting"""
        if BLACK_AVAILABLE:
            try:
                return black.format_str(code, mode=black.FileMode())
            except Exception as e:
                logging.warning(f"Black formatting failed: {e}")
                return self.basic_format_code(code)
        return self.basic_format_code(code)
    
    def basic_format_code(self, code):
        """Basic code formatting without black"""
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        indent_str = "    "
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Decrease indent for closing blocks
            if stripped.startswith(('class ', 'def ', '@')):
                indent_level = max(0, len(line) - len(line.lstrip())) // len(indent_str)
            
            formatted_lines.append(indent_str * indent_level + stripped)
        
        return '\n'.join(formatted_lines)
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        if PYPERCLIP_AVAILABLE:
            try:
                pyperclip.copy(text)
                return True
            except Exception as e:
                logging.warning(f"Pyperclip failed: {e}")
        
        # Fallback using tkinter
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
            root.destroy()
            return True
        except Exception as e:
            logging.error(f"Clipboard copy failed: {e}")
            return False
    
    def validate_dependencies(self, format_key, code):
        """Check if required dependencies are mentioned"""
        dependencies = {
            "customtkinter": ["customtkinter", "ctk"],
            "tkinter": ["tkinter", "tk"],
            "pyside6": ["PySide6", "PyQt6"],
            "html": []
        }
        
        missing = []
        for dep in dependencies.get(format_key, []):
            if f"import {dep}" not in code and f"from {dep}" not in code:
                missing.append(dep)
        
        return missing
        
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
        try:
            logging.info("Initializing Export Format Manager plugin...")
            self.app.event_manager.on(AppEvents.PROJECT_OPENED, self.setup)

        except Exception as e:
            logging.error(f"Error during Export Format Manager initialization: {e}")
        
    def setup(self):
        try:
            # Add to plugin menu
            logging.info("ExportFormatManager: Adding plugin button...")
            self.app.plugin_button_drop.add_separator()
            self.app.plugin_button_drop.add_option(
                "Export Format Manager", 
                self.open_format_manager
            )
            logging.info("ExportFormatManager: Plugin button added successfully")
            
            # Add to main menu
            logging.info("ExportFormatManager: Adding menu options...")
            self.app.menu_button_drop.add_separator()
            export_submenu = self.app.menu_button_drop.add_submenu("Export Formats", 4)
            
            for format_key, format_data in self.formats.items():
                export_submenu.add_option(
                    f"Export as {format_data['name']}", 
                    lambda fk=format_key: self.export_with_format(fk)
                )
            logging.info("ExportFormatManager: Menu options added successfully")
        except Exception as e:
            logging.error(f"ExportFormatManager: Error during initialization: {e}")
            raise
        
    def open_format_manager(self):
        """Open format manager window"""
        try:
            logging.info("ExportFormatManager: Opening format manager window...")
            
            if hasattr(self, 'window') and self.window.winfo_exists():
                self.window.lift()
                logging.info("ExportFormatManager: Bringing existing window to front")
                return
                
            self.window = CTk.CTkToplevel(self.app)
            self.window.title("Export Format Manager")
            self.window.geometry("900x700")
            self.window.resizable(True, True)
            
            logging.info("ExportFormatManager: Creating window widgets...")
            
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
            
            # Buttons frame
            button_frame = CTk.CTkFrame(top_frame)
            button_frame.pack(side="right", padx=5)
            
            CTk.CTkButton(
                button_frame,
                text="Export",
                command=self.export_current_format,
                width=80,
                fg_color=("green", "green")
            ).pack(side="left", padx=2)
            
            CTk.CTkButton(
                button_frame,
                text="Preview",
                command=self.preview_export,
                width=80
            ).pack(side="left", padx=2)
            
            CTk.CTkButton(
                button_frame,
                text="Validate",
                command=self.validate_current_export,
                width=80
            ).pack(side="left", padx=2)
            
            if PYPERCLIP_AVAILABLE:
                CTk.CTkButton(
                    button_frame,
                    text="📋 Copy",
                    command=self.copy_current_export,
                    width=80
                ).pack(side="left", padx=2)
            
            CTk.CTkButton(
                button_frame,
                text="History",
                command=self.show_history,
                width=80
            ).pack(side="left", padx=2)
            
            # Tabs for different sections
            tabview = CTk.CTkTabview(main_frame)
            tabview.pack(fill="both", expand=True)
            
            # Preview tab
            preview_tab = tabview.add("Preview")
            CTk.CTkLabel(preview_tab, text="Export Code Preview:", font=("Arial", 12, "bold")).pack(anchor="w", padx=5, pady=(5, 0))
            
            self.preview_text = CTk.CTkTextbox(preview_tab, font=("Courier", 9))
            self.preview_text.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Info tab
            info_tab = tabview.add("Info & Validation")
            self.info_text = CTk.CTkTextbox(info_tab, font=("Courier", 9), height=150)
            self.info_text.pack(fill="both", expand=True, padx=5, pady=5)
            
            logging.info("ExportFormatManager: Updating preview...")
            # Update preview
            self.update_preview()
            logging.info("ExportFormatManager: Format manager window opened successfully")
            
        except Exception as e:
            logging.error(f"ExportFormatManager: Error opening format manager window: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to open Format Manager:\n{e}")
        
    def on_format_change(self, format_key):
        """Handle format selection change"""
        self.current_format = format_key
        self.update_preview()
    
    def validate_current_export(self):
        """Validate the current export code"""
        try:
            code = self.generate_export_code(self.current_format)
            
            # Validate syntax
            valid, message = self.validate_python_code(code)
            
            info = f"=== VALIDATION REPORT ===\n\n"
            info += f"Format: {self.formats[self.current_format]['name']}\n"
            info += f"Status: {'✓ VALID' if valid else '✗ INVALID'}\n"
            info += f"Message: {message}\n"
            info += f"Code Lines: {len(code.splitlines())}\n"
            info += f"Code Size: {len(code)} bytes\n\n"
            
            # Check dependencies
            missing_deps = self.validate_dependencies(self.current_format, code)
            if missing_deps:
                info += f"⚠ Missing imports: {', '.join(missing_deps)}\n"
            else:
                info += f"✓ All expected imports present\n"
            
            if hasattr(self, 'info_text'):
                self.info_text.delete('1.0', 'end')
                self.info_text.insert('1.0', info)
            
            status_text = "✓ Code is valid!" if valid else f"✗ {message}"
            messagebox.showinfo("Validation Result", status_text) if valid else messagebox.showwarning("Validation Result", status_text)
            
        except Exception as e:
            messagebox.showerror("Validation Error", f"Error during validation: {e}")
    
    def copy_current_export(self):
        """Copy current export to clipboard"""
        try:
            code = self.generate_export_code(self.current_format)
            if self.copy_to_clipboard(code):
                self.app.cross_update_text_info(f"Code copied to clipboard ({len(code)} bytes)")
                messagebox.showinfo("Success", "Code copied to clipboard!")
            else:
                messagebox.showerror("Error", "Failed to copy to clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Copy failed: {e}")
    
    def show_history(self):
        """Show export history window"""
        if not self.export_history:
            messagebox.showinfo("History", "No exports recorded yet")
            return
        
        history_window = CTk.CTkToplevel(self.window)
        history_window.title("Export History")
        history_window.geometry("600x400")
        
        # Create text widget
        text_widget = CTk.CTkTextbox(history_window, font=("Courier", 10))
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Display history
        history_text = "=== EXPORT HISTORY ===\n\n"
        for i, record in enumerate(reversed(self.export_history[-20:]), 1):
            history_text += f"{i}. {record['timestamp']}\n"
            history_text += f"   Format: {record['format']}\n"
            history_text += f"   Status: {record['status']}\n"
            history_text += f"   File: {record['file_path']}\n\n"
        
        text_widget.insert('1.0', history_text)
        text_widget.configure(state='disabled')
        
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
            
            # Format code if available
            if BLACK_AVAILABLE:
                try:
                    preview_code = self.format_code(preview_code)
                except:
                    pass  # If formatting fails, show unformatted
            
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
        """Generate widget code based on format template with improved widget mapping"""
        widget_lines = []
        font_pattern = re.compile(r"<customtkinter\.windows\.widgets\.font\.ctk_font\.CTkFont object 'font\d{1,3}'>")
        font_pattern_ = re.compile(r'font\d{1,3}')
        
        # Get the mapping for current format
        format_key = self.current_format
        widget_type_mapping = self.widget_mapping_extended.get(format_key, {})

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

            # Try to map widget type if available
            mapped_widget_type = widget_type_mapping.get(widget_type, widget_type)

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
                    # Qt format with improved handling
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
                else:
                    widget_line = format_template["widget_no_name"].format(
                        widget_type=mapped_widget,
                        x=x, y=y
                    )
            elif widget_name:
                # Use widget name with mapped type
                widget_line = format_template["widget_template"].format(
                    widget_name=widget_name,
                    widget_type=mapped_widget_type,
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
                # No name - use widget_no_name template
                widget_line = format_template["widget_no_name"].format(
                    widget_type=mapped_widget_type,
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
            
            # Validate code (for Python formats)
            if format_key != "html":
                valid, message = self.validate_python_code(code)
                if not valid:
                    result = messagebox.askyesnocancel(
                        "Validation Warning", 
                        f"Code validation failed: {message}\n\nExport anyway?",
                        icon=messagebox.WARNING
                    )
                    if result is None or result is False:
                        self.add_to_history(format_key, file_path, "cancelled")
                        return
            
            # Format code if possible
            try:
                if format_key != "html":
                    code = self.format_code(code)
            except Exception as e:
                logging.warning(f"Code formatting skipped: {e}")
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Record in history
            self.add_to_history(format_key, file_path, "success")
            
            self.app.cross_update_text_info(f"✓ Exported as {format_template['name']}: {file_path}")
            messagebox.showinfo("Success", f"File exported successfully!\n\n📁 {file_path}\n📝 {len(code)} bytes")
            
        except Exception as e:
            logging.error(f"Export error: {e}")
            self.add_to_history(format_key, file_path, f"error: {str(e)}")
            messagebox.showerror("Export Error", f"Failed to export file:\n{e}")
            
    def preview_export(self):
        """Preview the export without saving"""
        self.update_preview()
        
        # Also show info
        if hasattr(self, 'info_text'):
            info = f"=== EXPORT INFO ===\n\n"
            info += f"Format: {self.formats[self.current_format]['name']}\n"
            info += f"Version: {self.version}\n"
            
            try:
                code = self.generate_export_code(self.current_format)
                info += f"Lines: {len(code.splitlines())}\n"
                info += f"Size: {len(code)} bytes\n\n"
                
                missing_deps = self.validate_dependencies(self.current_format, code)
                if missing_deps:
                    info += f"⚠ Missing imports: {', '.join(missing_deps)}\n"
                else:
                    info += f"✓ All dependencies present\n"
            except Exception as e:
                info += f"Error: {e}\n"
            
            self.info_text.delete('1.0', 'end')
            self.info_text.insert('1.0', info)
        
    def cleanup(self) -> None:
        """Cleanup when plugin is disabled"""
        self.save_formats()
        self.save_history()
        logging.info("Export Format Manager plugin v2.0.0 cleaned up successfully")