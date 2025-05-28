"""Import/export functionality for the virtual window."""

import json
import ast
import re
import logging
from data.variable import global_properties

class IOManagerMixin:
    """Handles file import/export operations."""
    
    def export_to_file(self, file_path):
        """Export window configuration to a file."""
        logging.info(f"Exporting to {file_path}")
        
        lines = self._generate_export_lines()
        self._write_lines_to_file(file_path, lines)
        
        self.app.cross_update_progressbar(1.0)
        self.app.cross_update_text_info(f"Export complete: {file_path}")
    
    def _generate_export_lines(self):
        """Generate lines of code for export."""
        self.app.cross_update_progressbar(0.0)
        
        window_params = self._get_window_params_string()
        self.app.cross_update_progressbar(0.5)
        
        lines = self._create_initial_lines(window_params)
        self._add_widget_lines(lines)
        
        self.app.cross_update_progressbar(0.7)
        lines.extend(self._create_footer_lines())
        
        return lines

    def _get_window_params_string(self):
        """Get window parameters as formatted string."""
        window_params = {
            "fg_color": self.cget("fg_color"),
            "bg_color": self.cget("bg_color"),
            "width": self.cget("width"),
            "height": self.cget("height"),
        }
        return ", ".join(f"{k}={repr(v)}" for k, v in window_params.items())

    def _create_initial_lines(self, window_params):
        """Create initial code lines."""
        include_comments = bool(self.app.config_manager.get("Export", "include_comments"))
        resizable = bool(self.app.config_manager.get("Export", "resizable"))
        
        return [
            *(['# Auto-generated code from VirtualWindow'] if include_comments else []),
            "import customtkinter as ctk",
            "",
            "class App(ctk.CTk):",
            "    def __init__(self):",
            "        super().__init__()",
            f"        self.geometry('{self.winfo_width()}x{self.winfo_height()}')",
            "        self.title('Exported Virtual Window')",
            "",
            f"        self.resizable({resizable},{resizable})",
            f"        self.virtual_window = ctk.CTkFrame(self, {window_params})",
            "        self.virtual_window.pack(expand=True, fill='both')",
            "        self.generic_widget_creator()",
            "",
            "    def generic_widget_creator(self):",
        ]

    def _add_widget_lines(self, lines):
        """Add widget creation code lines."""
        font_pattern = re.compile(r"<customtkinter\.windows\.widgets\.font\.ctk_font\.CTkFont object 'font\d{1,3}'>")
        font_pattern_ = re.compile(r'font\d{1,3}')
        
        if not self.widgets:
            lines.append("        pass")
            logging.warning("No widgets to export.")
            return
            
        for i, widget in enumerate(self.widgets):
            widget_type = widget.__class__.__name__
            widget_params = global_properties.get(widget_type)
            
            params_string = self._get_widget_params_string(widget, widget_params, font_pattern, font_pattern_)
            x, y = widget.winfo_x(), widget.winfo_y()
            
            if widget._name in self.left_sidebar.widget_dict:
                widget_name = self.left_sidebar.widget_dict[widget._name]
                lines.append(f"        self.{widget_name} = ctk.{widget_type}(self.virtual_window, {params_string})")
                lines.append(f"        self.{widget_name}.place(x={x}, y={y})")
            else:
                lines.append(f"        ctk.{widget_type}(self.virtual_window, {params_string}).place(x={x}, y={y})")
                
            self.app.cross_update_progressbar(0.2 + (0.6 * (i + 1) / len(self.widgets)))

    def _get_widget_params_string(self, widget, widget_params, font_pattern, font_pattern_):
        """Get widget parameters as formatted string."""
        params = []
        if widget_params:
            for value in widget_params:
                if value in (None, "", "default"):
                    continue
                    
                param_value = widget.cget(value)
                if value.lower() == "font" and (
                    font_pattern.match(str(param_value)) or 
                    font_pattern_.match(str(param_value))
                ):
                    logging.warning(f"Font parameter {param_value} will be skipped")
                    continue
                    
                params.append(f"{value}={repr(param_value)}")
                logging.info(f"Exporting: {value}={param_value}")
        else:
            logging.warning(f"No parameters found for widget {widget}")
            
        return ", ".join(params)

    def _create_footer_lines(self):
        """Create footer code lines."""
        return [
            "",
            "if __name__ == '__main__':",
            "    app = App()",
            "    app.mainloop()",
        ]

    def _write_lines_to_file(self, file_path, lines):
        """Write generated lines to file."""
        with open(file_path, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))
            logging.info("Successfully wrote code to file")

    def import_from_file(self, file_path):
        """Import window configuration from a file."""
        self.clean_virtual_window()
        
        try:
            code = self._read_file(file_path)
            if not code:
                return
                
            tree = ast.parse(code)
            self._process_import(tree)
            
        except Exception as e:
            logging.error(f"Import failed: {e}")
            self.app.cross_update_progressbar(0.0)

    def export_to_json(self, filename):
        """Export window state to JSON."""
        data = self.get_current_state()
        
        with open(f"{filename}.json", "w") as f:
            json.dump(data, f, indent=4)
            
    def import_from_json(self, filename):
        """Import window state from JSON."""
        self.clean_virtual_window()
        
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                
            for widget_data in data:
                self.create_and_place_widget(
                    widget_data["type"],
                    widget_data["properties"],
                    widget_data["x"],
                    widget_data["y"]
                )
                
        except Exception as e:
            logging.error(f"JSON import failed: {e}")