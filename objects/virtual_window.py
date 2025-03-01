import customtkinter as ctk
from data.variable import *
from functions.widget_resize import *
import tkinter as tk
import logging
import ast
import re

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

class VirtualWindow(ctk.CTkFrame):
    def __init__(self, parent, left_sidebar, app, parameters_dict:dict,width=800, height=500):
        super().__init__(parent, width=int(width), height=int(height), bg_color="lightgrey", fg_color="white")
        self.left_sidebar = left_sidebar
        self.app = app
        self.clipboard = ''
        self.widgets = []
        self.parameters_dict = parameters_dict
        self._is_hidden = False
        self._original_positions = {}
        
        self.guide_canvas = tk.Canvas(self, width=width, height=height, highlightthickness=0)
        self.guide_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        self.pack_propagate(False)
        self.make_widget_selectable(self)
        self.make_widget_selectable(self.guide_canvas)
        logging.info(f"VirtualWindow inicializada con dimensiones {self.cget('width')}x{self.cget('height')} y canvas configurado.")
        
    def count_widgets_by_type(self):
        """
        Cuenta la cantidad de widgets en una lista, clasificándolos por tipo.
        
        Args:
            widget_list (list): Lista de widgets de CustomTkinter.
        
        Returns:
            dict: Diccionario con el nombre del tipo de widget como clave
                y un subdiccionario con los nombres y la cantidad.
        """
        widget_count = {}
        
        for widget in self.widgets:
            widget_type = type(widget).__name__ 
            widget_name = widget._name if hasattr(widget, "_name") else "Unnamed"

            if widget_type not in widget_count:
                widget_count[widget_type] = {"count": 0, "names": []}

            widget_count[widget_type]["count"] += 1
            widget_count[widget_type]["names"].append(widget_name)
        
        return widget_count
    
    def replace(self):
        self.place(x=50, y=50)
    
    def add_widget(self, widget_type, **kwargs):
        """Agrega un widget al VirtualWindow."""
        logging.debug(f"Intentando agregar widget de tipo '{widget_type}'.")
        if widget := self.create_widget(widget_type, **kwargs):
            self._extracted_from_create_and_place_widget_5(widget, self.cget("width") / 2 - widget.cget("width") / 2 
                                                           , self.cget("height") / 2 - widget.cget("height")/2)
            logging.info(f"Widget de tipo '{widget_type}' agregado en posición inicial {widget.cget('width')} {widget.cget('height')}")
        else:
            logging.warning(f"Fallo al agregar widget de tipo '{widget_type}'.")

    def create_widget(self, widget_type, **kwargs):
        """Crea un widget basado en el tipo proporcionado."""
        logging.debug(f"Creando widget de tipo '{widget_type}' con argumentos: {kwargs}.")
        if widget_class := widget_classes.get(widget_type):
            widget = widget_class(self, **kwargs)
            logging.info(f"Widget '{widget_type}' creado con éxito.")
            return widget
        logging.error(f"'{widget_type}' no es un tipo de widget válido.")
        return None
    
    def paste_widget(self, widget, **kwargs):
        """Agrega un widget al VirtualWindow con los argumentos proporcionados."""
        logging.debug(f"Agregando widget de tipo '{widget.__class__.__name__}' con argumentos: {kwargs}.")
        self.add_widget(widget.__class__.__name__, **kwargs)
        logging.info(f"Widget de tipo '{widget.__class__.__name__}' agregado en posición inicial {widget.cget('width')} {widget.cget('height')}")
    
    def toggle_visibility(self):
        """Alterna la visibilidad de todos los widgets dentro de la VirtualWindow."""
        if self._is_hidden:
            for widget in self.widgets:
                if widget in self._original_positions:
                    x, y = self._original_positions[widget]
                    widget.place(x=x, y=y)
            self._is_hidden = False
            logging.info("Widgets desocultados.")
        else:
            for widget in self.widgets:
                self._original_positions[widget] = (widget.winfo_x(), widget.winfo_y())
                widget.place_forget()
            self._is_hidden = True
            logging.info("Widgets ocultados.")
        return self._is_hidden
    
    def previsualize_code(self):
        logging.debug("Intentando generar lineas")

        lines = self._extracted_from_export_to_file_4()
        self.update_idletasks()

        lines.extend(self.create_footer_lines())
        self.app.cross_update_progressbar(1.0)
        self.update_idletasks()
        return lines
    
    def export_to_file(self, file_path):
        """Exports the current virtual window configuration to a specified file."""
        logging.debug(f"Attempting to export file to {file_path}.")

        lines = self._extracted_from_export_to_file_4()
        lines.extend(self.create_footer_lines())

        self.write_to_file(file_path, lines)
        self.app.cross_update_progressbar(1.0)
        self.update_idletasks()
        self.app.cross_update_text_info(f"Export complete, Directory: {file_path}")
        logging.info("Export completed.")

    # TODO Rename this here and in `previsualize_code` and `export_to_file`
    def _extracted_from_export_to_file_4(self):
        self.app.cross_update_progressbar(0.0)
        self.update_idletasks()
        window_params_string = self.get_window_params_string()
        self.app.cross_update_progressbar(0.5)
        self.update_idletasks()
        result = self.create_initial_lines(window_params_string)
        self.add_widget_lines(result)
        self.app.cross_update_progressbar(0.7)
        return result

    def get_window_params_string(self):
        """Retrieves the window parameters as a formatted string."""
        window_params = {
            "fg_color": self.cget("fg_color"),
            "bg_color": self.cget("bg_color"),
            "width": self.cget("width"),
            "height": self.cget("height"),
        }
        logging.debug("Loading window parameters...")
        return ", ".join(f"{k}={repr(v)}" for k, v in window_params.items())

    def create_initial_lines(self, window_params_string):
        """Creates the initial lines of the exported code."""
        logging.debug("Creating initial lines...")
        heredate = "class App(ctk.CTk):" if self.parameters_dict.get('is_scene_manager') else "class App(ctk.CTk):"
        logging.info("Applying inheritance from Base Scene" if self.parameters_dict.get('is_scene_manager') else "Not using Base Scene")

        return [
            "# Auto-generated code from a VirtualWindow",
            "import customtkinter as ctk",
            "",
            heredate,
            "    def __init__(self):",
            "        super().__init__()",
            f"        self.geometry('{self.winfo_width()}x{self.winfo_height()}')",
            "        self.title('Exported Virtual Window')",
            "",
            f"        self.resizable({bool(self.parameters_dict.get('is_resizable'))},{bool(self.parameters_dict.get('is_resizable'))})",
            f"        self.virtual_window = ctk.CTkFrame(self, {window_params_string})",
            "        self.virtual_window.pack(expand=True, fill='both')",
            "        self.generic_widget_creator()",
            "",
            "    def generic_widget_creator(self):",
        ]

    def add_widget_lines(self, lines):
        """Adds lines for each widget to the exported code."""
        font_pattern = re.compile(r"<customtkinter\.windows\.widgets\.font\.ctk_font\.CTkFont object 'font\d{1,3}'>")
        font_pattern_ = re.compile(r'font\d{1,3}')

        total_widgets = len(self.widgets)
        for i, widget in enumerate(self.widgets):
            widget_type = widget.__class__.__name__
            widget_params = global_properties.get(widget.__class__.__name__)

            x = widget.winfo_x()
            y = widget.winfo_y()

            params_string = self.get_widget_params_string(widget, widget_params, font_pattern, font_pattern_)
            print(self.left_sidebar.widget_dict.values())
            if widget._name in self.left_sidebar.widget_dict:
                logging.info("Exporting: Utilizing name for widget ")
                lines.append(f"        self.{self.left_sidebar.widget_dict[widget._name]} = ctk.{widget_type}(self.virtual_window, {params_string})")
                lines.append(f"        self.{self.left_sidebar.widget_dict[widget._name]}.place(x={x}, y={y})")
            else:
                lines.append(f"        ctk.{widget_type}(self.virtual_window, {params_string}).place(x={x}, y={y})")
            self.app.cross_update_progressbar(0.2 + (0.6 * (i + 1) / total_widgets))
            self.update_idletasks()

    def get_widget_params_string(self, widget, widget_params, font_pattern, font_pattern_):
        """Retrieves the widget parameters as a formatted string."""
        params = []
        if widget_params is not None:
            for value in widget_params:
                if value not in (None, "", "default"):
                    param_value = widget.cget(value)
                    if value.lower() == "font" and (font_pattern.match(str(param_value)) or font_pattern_.match(str(param_value))):
                        logging.warning(f"The 'font' parameter with value {param_value} will not be exported.")
                        continue
                    params.append(f"{value}={repr(param_value)}")
                    logging.info(f"Exporting: {value}={param_value}")
        else:
            logging.warning(f"Error: Widget parameters are 'None' for {widget}")

        return ", ".join(params)

    def create_footer_lines(self):
        """Creates the footer lines for the exported code."""
        return [
            "",
            "if __name__ == '__main__':",
            "    app = App()",
            "    app.mainloop()",
        ]

    def write_to_file(self, file_path, lines):
        """Writes the generated lines to the specified file."""
        logging.info("Successfully created lines. Writing to file...")
        with open(file_path, "w", encoding="utf-8") as file:
            logging.info("\n".join(lines))
            file.write("\n".join(lines))

    def make_widget_movable(self, widget):
        """Hace que un widget sea movible dentro del VirtualWindow con líneas guía."""
        def start_move(event):
            widget._drag_start_x = event.x
            widget._drag_start_y = event.y
            self.clear_guides()

        def do_move(event):
            new_x = widget.winfo_x() + event.x - widget._drag_start_x
            new_y = widget.winfo_y() + event.y - widget._drag_start_y
            widget.place(x=new_x, y=new_y)

            self.clear_guides()
            self.draw_guides(widget, new_x, new_y)

            if hasattr(self.left_sidebar, 'update_positions'):
                self.left_sidebar.update_positions(new_x, new_y)

        def stop_move(event):
            self.clear_guides()

        widget.bind("<Button-1>", start_move)
        widget.bind("<B1-Motion>", do_move)
        widget.bind("<ButtonRelease-1>", stop_move)

    def add_custom_widget(self, widget):
        """Agrega un widget personalizado a la VirtualWindow."""
        self.add_widget(widget)

    def draw_guides(self, widget, new_x, new_y, show_guides=True, color_exact="green", color_near="red", tolerance=5, snap_range=10):
        """Draws guide lines on the canvas to assist with alignment and snaps the widget if it's near a guide.

        Args:
            widget: The widget being moved.
            new_x: The new x position of the widget.
            new_y: The new y position of the widget.
            show_guides: Boolean to show or hide the guides.
            color_exact: Color of the guides when exactly aligned.
            color_near: Color of the guides when near alignment.
            tolerance: Tolerance to consider widgets aligned.
            snap_range: Range at which the widget snaps when near a guide.
        """
        if not show_guides:
            return

        widget_width = widget.winfo_width()
        widget_height = widget.winfo_height()

        widget_center_x = new_x + widget_width // 2
        widget_center_y = new_y + widget_height // 2

        for child in self.widgets:
            if child == widget:
                continue

            child_x = child.winfo_x()
            child_y = child.winfo_y()
            child_width = child.winfo_width()
            child_height = child.winfo_height()
            child_center_x = child_x + child_width // 2
            child_center_y = child_y + child_height // 2

            # Define a helper function to draw guide lines
            def draw_guide(x1, y1, x2, y2, color, condition):
                if condition:
                    self.create_guide_line(x1, y1, x2, y2, color)

            # Vertical Centering
            draw_guide(child_center_x, 0, child_center_x, self.winfo_height(), color_exact, widget_center_x == child_center_x)
            draw_guide(child_center_x, 0, child_center_x, self.winfo_height(), color_near, abs(widget_center_x - child_center_x) <= tolerance)
            if abs(widget_center_x - child_center_x) <= snap_range:
                new_x = child_center_x - widget_width // 2

            # Horizontal Centering
            draw_guide(0, child_center_y, self.winfo_width(), child_center_y, color_exact, widget_center_y == child_center_y)
            draw_guide(0, child_center_y, self.winfo_width(), child_center_y, color_near, abs(widget_center_y - child_center_y) <= tolerance)
            if abs(widget_center_y - child_center_y) <= snap_range:
                new_y = child_center_y - widget_height // 2

            # Left and Right Edges
            draw_guide(child_x, 0, child_x, self.winfo_height(), color_exact, new_x == child_x)
            draw_guide(child_x, 0, child_x, self.winfo_height(), color_near, abs(new_x - child_x) <= tolerance)
            if abs(new_x - child_x) <= snap_range:
                new_x = child_x

            draw_guide(child_x + child_width, 0, child_x + child_width, self.winfo_height(), color_exact, new_x + widget_width == child_x + child_width)
            draw_guide(child_x + child_width, 0, child_x + child_width, self.winfo_height(), color_near, abs(new_x + widget_width - (child_x + child_width)) <= tolerance)
            if abs(new_x + widget_width - (child_x + child_width)) <= snap_range:
                new_x = child_x + child_width - widget_width

            # Top and Bottom Edges
            draw_guide(0, child_y, self.winfo_width(), child_y, color_exact, new_y == child_y)
            draw_guide(0, child_y, self.winfo_width(), child_y, color_near, abs(new_y - child_y) <= tolerance)
            if abs(new_y - child_y) <= snap_range:
                new_y = child_y

            draw_guide(0, child_y + child_height, self.winfo_width(), child_y + child_height, color_exact, new_y + widget_height == child_y + child_height)
            draw_guide(0, child_y + child_height, self.winfo_width(), child_y + child_height, color_near, abs(new_y + widget_height - (child_y + child_height)) <= tolerance)
            if abs(new_y + widget_height - (child_y + child_height)) <= snap_range:
                new_y = child_y + child_height - widget_height

        widget.place(x=new_x, y=new_y)

    def create_guide_line(self, x1, y1, x2, y2, color):
        """Crea una línea guía en el canvas."""
        self.guide_canvas.create_line(x1, y1, x2, y2, fill=color, dash=(4, 2), width=1)

    def clear_guides(self):
        """Elimina las líneas guía del canvas."""
        self.guide_canvas.delete("all")

    def make_widget_selectable(self, widget):
        """Hace que un widget sea seleccionable con clic derecho."""
        logging.info(f"Creando widget seleccionable {widget.__class__.__name__} ")
        try:
            def select_widget(event):
                logging.info(f"{widget.__class__.__name__} seleccionado.")
                if widget.__class__.__name__ == "Canvas":
                    self.left_sidebar.show_widget_config(self)
                    widget.bind("<Button-3>", lambda event: select_widget(event))
                else:
                    self.left_sidebar.show_widget_config(widget)
                    enable_resizable_highlight(self.guide_canvas,widget, self.left_sidebar)
                    
            def copy(widget):
                self.clipboard = widget
                logging.info(f"{widget.__class__.__name__} copied.")
                
            def paste():
                if self.clipboard:
                    self.app.inter_add_widget(self.clipboard)
                    logging.info(f"{self.clipboard.__class__.__name__} pasted.")
                else:
                    logging.info("No hay widget seleccionado para pegar.")

            # Asignar manejadores de eventos
            widget.bind("<Button-3>", select_widget)  # Clic derecho
            widget.bind("<Delete>", lambda event: self.left_sidebar.delete_widget(widget))  # Delete
            widget.bind("<Control-c>", lambda event: copy(widget))  # Ctrl + C
            widget.bind("<Control-v>", lambda event: paste())  # Ctrl + V
            if widget.__class__.__name__ != "Canvas":
                enable_resizable_highlight(self.guide_canvas,widget, self.left_sidebar)
            logging.info(f"Widget {widget.__class__.__name__} seleccionable creado.")
        except Exception as e:
            logging.error(f"Error en la selección de widget: {e}")

    def delete_widget(self, widget):
        """Borra un widget del VirtualWindow."""
        widget.destroy()
        self.widgets.remove(widget)
        logging.debug(f"Deleted widget:{widget}")
        
    def clean_virtual_window(self):
        """Limpia el contenido del VirtualWindow."""
        logging.info("Limpiando el contenido del VirtualWindow.")
        try:
            self.clear_guides()
            for widget in self.widgets:
                self.left_sidebar.delete_widget(widget)
            logging.info("El contenido del VirtualWindow fue borrado correctamente.")
        except Exception as e:
            logging.error(f"Error al limpiar el contenido del VirtualWindow: {e}")
        
    # ----------------------------------------------------------------
    # Métodos de importación de widgets desde código
    # ----------------------------------------------------------------    
    
    def import_from_codebox(self, code):
        """Importa widgets desde el código proporcionado en CodeBox, incluidos sus parámetros."""
        self.clean_virtual_window()
        logging.info("Iniciando la importación de widgets desde CodeBox")
        try:
            if not code:
                logging.error("El código proporcionado está vacío, abortando la importación.")
                self.app.cross_update_text_info("El código proporcionado está vacío, abortando.")
                return

            tree = ast.parse(code)
            self.app.cross_update_progressbar(0.2)

            app_class = self.find_app_class(tree)
            self.app.cross_update_progressbar(0.4) 

            if not app_class:
                logging.error("No se encontró la clase 'App', abortando la importación.")
                return

            if generic_widget_creator := self.find_generic_widget_creator(app_class):
                self._extracted_from_import_from_file_22(generic_widget_creator)
            else:
                logging.error("No se encontró la función 'generic_widget_creator', abortando la importación.")

            logging.info("Importación completada exitosamente.")
            self.app.cross_update_text_info("Importación completada exitosamente.")
            self.app.cross_update_progressbar(1.0)
        except Exception as e:
            logging.error(f"Error durante la importación: {e}")
            self.app.cross_update_progressbar(0.0)    
        
    def import_from_file(self, file_path):
        """Importa widgets desde un archivo Python exportado, incluidos sus parámetros."""
        self.clean_virtual_window()
        logging.info(f"Iniciando la importación de widgets desde el archivo: {file_path}")
        try:
            code = self.read_file(file_path)
            if code is None:
                logging.error("No se pudo leer el archivo, abortando la importación.")
                self.app.cross_update_text_info("No se pudo leer el archivo, abortando.")
                return

            tree = ast.parse(code)

            if geometry := self.detect_window_geometry(tree):
                width, height, x, y = geometry
                self.configure(width=width, height=height)
                logging.info(f"Geometría detectada: {width}x{height}+{x}+{y}")

            self.app.cross_update_progressbar(0.2)

            app_class = self.find_app_class(tree)
            self.app.cross_update_progressbar(0.4) 

            if not app_class:
                logging.error("No se encontró la clase 'App', abortando la importación.")
                return

            if generic_widget_creator := self.find_generic_widget_creator(app_class):
                self._extracted_from_import_from_file_22(generic_widget_creator)
            else:
                logging.error("No se encontró la función 'generic_widget_creator', abortando la importación.")

            logging.info("Importación completada exitosamente.")
            self.app.cross_update_text_info("Importación completada exitosamente.")
            self.app.cross_update_progressbar(1.0)
        except Exception as e:
            logging.error(f"Error durante la importación: {e}")
            self.app.cross_update_progressbar(0.0) 
            
    def detect_window_geometry(self, tree):
        """Detecta la geometría de la ventana en el código importado."""
        logging.info("Buscando geometría de la ventana en el código importado")
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                func = node.value.func
                if isinstance(func, ast.Attribute) and func.attr == "geometry":
                    try:
                        geometry_str = ast.literal_eval(node.value.args[0])
                        if match := re.match(
                            r"(\d+)x(\d+)\+?(\d+)?\+?(\d+)?", geometry_str
                        ):
                            width, height, x, y = match.groups()
                            return int(width), int(height), int(x or 0), int(y or 0)
                    except Exception as e:
                        logging.warning(f"No se pudo interpretar la geometría: {e}")
                        return None
        logging.warning("No se encontró ninguna asignación de geometría en el código.")
        return None

    # TODO Rename this here and in `import_from_codebox` and `import_from_file`
    def _extracted_from_import_from_file_22(self, generic_widget_creator):
        logging.info(
            "Se encontró la función 'generic_widget_creator', procesando llamadas de widgets."
        )
        self.process_widget_calls(generic_widget_creator)
        self.app.cross_update_progressbar(0.8) 

    def read_file(self, file_path):
        """Lee el contenido del archivo especificado."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                logging.debug(f"Archivo {file_path} leído correctamente.")
                return file.read()
        except Exception as e:
            logging.error(f"Error al leer el archivo {file_path}: {e}")
            return None

    def find_app_class(self, tree):
        """Encuentra la clase 'App' en el AST."""
        app_class = next((node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "App"), None)
        if not app_class:
            logging.warning("No se encontró ninguna clase llamada 'Aplicación'.")
        else:
            logging.debug("Clase 'App' encontrada en el AST.")
        return app_class

    def find_generic_widget_creator(self, app_class):
        """Encuentra la función 'generic_widget_creator' en la clase 'App'."""
        generic_widget_creator = next(
            (subnode for subnode in app_class.body if isinstance(subnode, ast.FunctionDef) and subnode.name == "generic_widget_creator"),
            None,
        )
        if not generic_widget_creator:
            logging.warning("No se encontró ninguna función denominada 'generic_widget_creator'.")
        else:
            logging.debug("Función 'generic_widget_creator' encontrada en la clase 'App'.")
        return generic_widget_creator

    def process_widget_calls(self, generic_widget_creator):
        """Procesa llamadas de widgets en la función 'generic_widget_creator'."""
        logging.info("Procesando llamadas de widgets en 'generic_widget_creator'.")
        for stmt in generic_widget_creator.body:
            if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)):
                logging.debug("Declaración ignorada, no es una llamada de widget.")
                continue

            widget_call = stmt.value
            if not (isinstance(widget_call.func, ast.Attribute) and isinstance(widget_call.func.value, ast.Call)):
                logging.debug("Llamada de widget ignorada, no es una llamada válida.")
                continue

            widget_type = widget_call.func.value.func.attr
            widget_method = widget_call.func.attr

            if widget_method != "place":
                logging.debug(f"Método '{widget_method}' ignorado, solo se procesan métodos 'place'.")
                continue

            widget_args, placement_args = self.extract_widget_args(widget_call)
            x = placement_args.get("x", 0)
            y = placement_args.get("y", 0)

            logging.debug(f"Creando y colocando widget de tipo '{widget_type}' en ({x}, {y}).")
            self.create_and_place_widget(widget_type, widget_args, x, y)

    def extract_widget_args(self, widget_call):
        """Extrae argumentos de widget y ubicación de la llamada del widget."""
        logging.debug("Extrayendo argumentos de widget y ubicación.")
        widget_args = {
            kw.arg: ast.literal_eval(kw.value)
            for kw in widget_call.func.value.keywords
            if kw.arg in global_properties.get(widget_call.func.value.func.attr, [])
        }

        placement_args = {
            kw.arg: ast.literal_eval(kw.value)
            for kw in widget_call.keywords
        }
        logging.debug(f"Argumentos de widget extraídos: {widget_args}, Argumentos de ubicación: {placement_args}.")
        return widget_args, placement_args

    def create_and_place_widget(self, widget_type, widget_args, x, y):
        """Crea y coloca el widget y actualiza la lista de widgets."""
        logging.debug(f"Intentando crear el widget del tipo '{widget_type}' con argumentos: {widget_args}.")
        if widget := self.create_widget(widget_type, **widget_args):
            self._extracted_from_create_and_place_widget_5(widget, x, y)
            logging.info(f"Widget del tipo '{widget_type}' ubicado en ({x}, {y}).")
        else:
            logging.error(f"No se pudo crear el widget del tipo '{widget_type}'.")

    def _extracted_from_create_and_place_widget_5(self, widget, x, y):
        widget.place(x=x, y=y)
        self.make_widget_movable(widget)
        self.make_widget_selectable(widget)
        self.widgets.append(widget)
