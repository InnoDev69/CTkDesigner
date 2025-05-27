# Version: 1.2
# Tiene comentarios en español y a veces en ingles, depende el dia

import io
import sys
import logging
import tkinter as tk
import tkinter.ttk as ttk
from data.commands import *
import customtkinter as ctk
from functions.sidebars_utils import *
from tkinter import filedialog
from functions.generic import *
from functions.import_widget import *
from CTkMessagebox import CTkMessagebox
from objects.code_box import CTkCodeBox
from translations.translations import *
from config.config_manager import ConfigManager
from functions.create_widget_animation import *
from objects.virtual_window import VirtualWindow
#BETA
from objects.theme_manager import ThemeManager
from objects.CTkMenuBar import *
#from functions.translator_manager import *
#from objects.zoomable_canvas import ZoomableCanvas

class LeftSidebar(ctk.CTkScrollableFrame):
    PADDING = 5
    ROW_SCENE = 0

    def __init__(self, parent):
        self.widget_dict = {}
        
        super().__init__(parent, width=200)
        self.grid_columnconfigure(0, weight=1)

        self.widget_config_scrollable = self.create_scrollable_frame()
        self.widget_config_label = self.create_label(self.widget_config_scrollable,
            app.translator.translate("CONFIG_LABEL_TEXT")
        )

        self.config_space = self.create_config_space()
        if app.use_scene_manager:
            self.scene_manager_frame = self.create_scene_manager_frame()

    def update_positions(self, x:int, y:int):
        if hasattr(self, "x_entry") and hasattr(self, "y_entry"):
            self.x_entry.delete(0, "end")
            self.y_entry.delete(0, "end")
            self.x_entry.insert(0,str(x))
            self.y_entry.insert(0,str(y))

    def create_scrollable_frame(self):
        """
        Crea un Scrollable Frame para mostrar widgets.

        Parámetros:
        Ninguno

        Retorna:
        frame (ctk.CTkScrollableFrame o ctk.CTkFrame): Un marco desplazable o un marco regular, dependiendo del valor de app.use_scene_manager.
        """
        frame = ctk.CTkScrollableFrame(self, width=200, height=350, fg_color='#292929') if app.use_scene_manager else ctk.CTkFrame(self, fg_color='#292929')
        return self._extracted_from_create_scene_manager_frame_3(frame)

    def create_label(self, parent, text:str):
        """
        Crea y configura un widget CTkLabel.

        Esta función crea un nuevo widget CTkLabel con el texto proporcionado,
        lo agrega al widget padre especificado y configura su posición en la cuadrícula.

        Parámetros:
        parent (ctk.CTk): El widget padre al que se agregará el Label.
        text (str): El texto que se mostrará en el Label.

        Retorna:
        ctk.CTkLabel: El Label creado y configurado.
        """
        label = ctk.CTkLabel(parent, text=text)
        label.grid(row=0, column=0, padx=self.PADDING, pady=self.PADDING)
        return label

    def create_config_space(self):
        """Create the configuration space frame.

        Returns:
            ctk.CTkFrame: The config space frame.
        """
        config_space = ctk.CTkFrame(self.widget_config_scrollable, fg_color='#292929')
        return self._extracted_from_create_scene_manager_frame_3(config_space)

    def create_scene_manager_frame(self):
        """Create the scene manager frame.

        Returns:
            ctk.CTkScrollableFrame: The scene manager frame.
        """

        frame = ctk.CTkScrollableFrame(self, fg_color='#292929')
        return self._extracted_from_create_scene_manager_frame_3(frame)

    def add_to_scene_manager_frame(self, arg0):
        self._extracted_from_create_scene_manager_frame_3(arg0)

    def _extracted_from_create_scene_manager_frame_3(self, arg0:object):
        """Grid a widget and update row count.

        Args:
            arg0: The widget to grid.

        Returns:
            The gridded widget.
        """

        arg0.grid(
            row=self.ROW_SCENE, column=0, sticky="nsew", padx=self.PADDING, pady=self.PADDING
        )
        self.ROW_SCENE += 1
        arg0.grid_columnconfigure(0, weight=1)
        return arg0

    def add_widget_to_grid(self, widget:object, row:int, column:int, **grid_options:dict):
        widget.grid(in_=self.grid_frame, row=row, column=column, **grid_options)

    def show_widget_config(self, widget:object):
        """Display configuration options for a widget.

        Clears the existing configuration space and populates it with the settings for the given widget.  This includes property entries, position entries, and action buttons.

        Args:
            widget: The widget to configure.
        """
        clear_widgets(self.config_space)
        widget.focus_set()
        widget_properties = global_properties
        widget_type = widget.__class__.__name__
        app.cross_update_text_info(f"{app.translator.translate('USER_SHOW_WIDGET_CONFIG')} {widget_type}")
        logging.debug(get_class_parameters(widget.__class__)[1:])
        if widget.__class__.__name__ not in widget_classes:
            self.create_property_entries(widget, get_class_parameters(widget.__class__)[1:])
        else:
            self.create_property_entries(widget, widget_properties[widget_type])
        self.create_position_entries(widget)
        self.create_action_buttons(widget)

    def update_weights(self, w, h):
        self.height_entry.delete(0, "end")
        self.width_entry.delete(0, "end")
        self.height_entry.insert(0,int(h))
        self.width_entry.insert(0,int(w))
    
    def create_property_entries(self, widget: object, properties: list):
        """Create property entries for widget configuration."""
        if not hasattr(self, "property_entries"):
            self.property_entries = {}

        entries = create_property_entries(
            self.config_space, 
            widget, 
            properties, 
            self.update_property, 
            self.property_entries
        )
        
        if 'width' in entries:
            self.width_entry = entries['width']
        if 'height' in entries:
            self.height_entry = entries['height']
            
        self.property_entries.update(entries)
        
    def update_property(self, widget: object, prop: str, entry: object, tooltip: object):
        # sourcery skip: de-morgan
        """Update a widget property based on entry value."""
        tooltip.hide()
        try:
            current_value = widget.cget(prop)
            if not entry.__class__.__name__ == "CTkButton":
                if isinstance(entry.get(), str):
                    new_value = entry.get().strip()
                else:
                    new_value = entry.cget("state").strip()
            else:
                text_value = entry.cget("text")
                new_value = ''.join(text_value) if isinstance(text_value, list) else str(text_value).strip()

            if str(current_value) == new_value:
                logging.debug(f"No se requiere actualización para '{prop}'. El valor no ha cambiado.")
                return

            if "color" in prop:
                if isinstance(new_value, list):
                    new_value = ''.join(new_value)
                new_value = fix_color_format(new_value)
                widget.configure(**{prop: new_value})
            else:
                type_of_property = str if prop == "text_color" else type(current_value)
                if prop == "font":
                    self.update_font_property(widget, entry)
                elif widget.__class__.__name__ == "VirtualWindow" and prop == "fg_color":
                    widget.configure(**{prop: type_of_property(new_value)})
                    widget.guide_canvas.config(bg=new_value)
                else:
                    widget.configure(**{prop: type_of_property(new_value)})

            app.cross_update_text_info(app.translator.translate_with_vars("USER_PROP_UPDATED", 
                        {"prop": prop, "widget": widget, "entry": new_value}))
            entry.configure(border_color="#565B5E")
            
        except Exception as e:
            app.cross_update_text_info(f"Error al actualizar '{prop}': {e}. Valor ingresado: {entry.get()}")
            entry.configure(border_color="red")
            tooltip.show()
            tooltip.configure(message=str(e))

    def update_font_property(self, widget:object, entry:object):
        font_value = entry.get()
        font_parts = font_value.rsplit(" ", 1)
        if len(font_parts) != 2 or not font_parts[1].isdigit():
            raise ValueError(f"El valor '{font_value}' no es válido para 'font'. Formato esperado: 'Arial 20'")
        font_name, font_size = font_parts[0], int(font_parts[1])
        widget.configure(font=(font_name, font_size))
        app.cross_update_text_info(app.translator.translate_with_vars("USER_PROP_FONT_UPDATED", {"font_name": font_name, "font_size": font_size}))

    def create_position_entries(self, widget:object):
        """Create position entries for the widget.

        Creates entry widgets for the x and y coordinates of the widget, and an entry for a variable name.  Binds key release events to update functions.

        Args:
            widget: The widget.
        """

        position_frame = self._extracted_from_create_position_entries_2(
            "POSITION_LABEL_TEXT"
        )
        self.x_entry = self.create_position_entry(position_frame, widget.winfo_x())
        self.y_entry = self.create_position_entry(position_frame, widget.winfo_y())

        position_var_frame = self._extracted_from_create_position_entries_2(
            "RIGHTBAR_BUTTON_VARIABLE_NAME"
        )
        widget_var = self.create_position_entry(position_var_frame, '', width=110)

        self.x_entry.bind("<KeyRelease>", lambda event: self.update_position(widget, self.x_entry, self.y_entry))
        self.y_entry.bind("<KeyRelease>", lambda event: self.update_position(widget, self.x_entry, self.y_entry))
        widget_var.bind("<KeyRelease>", lambda event: self.variable_widget_change(widget._name, widget_var))

    # TODO Rename this here and in `create_position_entries`
    def _extracted_from_create_position_entries_2(self, arg0:str):
        """Create a labeled frame for position entries.

        Creates a CTkFrame and adds a CTkLabel above it with translated text.

        Args:
            arg0: Label text key.

        Returns:
            ctk.CTkFrame: The frame.
        """

        ctk.CTkLabel(self.config_space, text=app.translator.translate(arg0)).pack(
            pady=self.PADDING
        )
        result = ctk.CTkFrame(self.config_space)
        result.pack(pady=self.PADDING)

        return result

    def variable_widget_change(self, widget:object, widget_var:str):
        """Handle changes in the widget variable name.

        Attempts to update the widget's variable name; if the entered name is invalid, it logs a warning and corrects the name to contain only alphabetic characters.

        Args:
            widget: The widget name.
            widget_var: The variable name entry.
        """

        var_name = widget_var.get()
        if self.update_variable_name(widget, widget_var):
            app.cross_update_text_info(app.translator.translate("USER_VAR_UPDATED"))
        else:
            corrected_var_name = ''.join(filter(str.isalpha, var_name))
            widget_var.delete(0, 'end')
            widget_var.insert(0, corrected_var_name)
            logging.warning(f"El nombre de la variable '{var_name}' no es válido. Se ha corregido a '{corrected_var_name}'.")

    def update_variable_name(self, widget:object, widget_var:str):
        """Update the variable name associated with the widget.

        Stores the variable name in the widget dictionary if it's valid (alphabetic or empty).

        Args:
            widget: The widget name.
            widget_var: The variable name entry.

        Returns:
            bool: True if the variable name is valid, False otherwise.
        """

        var_name = widget_var.get()
        if var_name.isalpha() or var_name == '':
            self.widget_dict[widget] = var_name
            return True
        else:
            return False

    def create_position_entry(self, parent, initial_value:int, width:int=50):
        """Create an entry for position values.

        Creates a CTkEntry widget with a specified width and initial value, and packs it to the left.

        Args:
            parent: The parent widget.
            initial_value: The initial value.
            width: The entry width.

        Returns:
            ctk.CTkEntry: The created entry widget.
        """

        entry = ctk.CTkEntry(parent, width=width)
        entry.insert(0, initial_value)
        entry.pack(side="left", padx=2)
        return entry

    def update_position(self, widget:object, x_entry:int, y_entry:int):
        """Update the position of a widget.

        Tries to update the widget's position using values from x and y entry widgets. Logs a warning if the entry values are not valid integers.

        Args:
            widget: The widget to move.
            x_entry: The entry widget containing the x-coordinate.
            y_entry: The entry widget containing the y-coordinate.
        """

        try:
            new_x = int(x_entry.get())
            new_y = int(y_entry.get())
            widget.place(x=new_x, y=new_y)
            app.cross_update_text_info(app.translator.translate_with_vars("USER_POS_UPDATED", {"new_x": new_x, "new_y": new_y}))
        except ValueError:
            logging.warning("Posición inválida. Por favor, ingresa valores numéricos.")

    def create_action_buttons(self, widget:object): 
        """Create action buttons for the widget.

        Creates buttons for raising, lowering, and deleting the given widget, adding them to the configuration space.  Button labels are translated using the app translator.

        Args:
            widget: The widget for which to create action buttons.
        """

        actions = [ 
            (app.translator.translate("RIGHTBAR_BUTTON_UPLOAD_LAYER"), lambda: widget.lift()), 
            (app.translator.translate("RIGHTBAR_BUTTON_LOWER_LAYER"), lambda: widget.lower()), 
            (app.translator.translate("RIGHTBAR_BUTTON_DELETE_WIDGET"), lambda: self.delete_widget(widget)),
        ]
        for text, command in actions:
            ctk.CTkButton(self.config_space, text=text, command=command, **BUTTON_STYLE).pack(pady=15)

    def delete_widget(self, widget:object):
        """Delete a widget.

        Deletes the given widget from the virtual window, clears the config space, and updates the treeview, unless the widget is the virtual window itself.  Logs an error if attempting to delete the virtual window.

        Args:
            widget: The widget to delete.
        """

        if widget.__class__.__name__ != 'VirtualWindow':
            app.virtual_window.delete_widget(widget)
            clear_widgets(self.config_space)
            app.cross_update_treeview()
        else:
            app.cross_update_text_info("No se puede borrar la virtual window")

class RightSidebar(ctk.CTkScrollableFrame):
    TREEVIEW_WIDTH = 180
    PADDING = 5

    def __init__(self, parent, virtual_window):
        super().__init__(parent, width=200)
        self.configure_treeview_style()
        self.grid_columnconfigure(0, weight=1)
        self.virtual_window = virtual_window
        self.widget_tree = {}
        self.buttons = {}

        self.create_widgets_section()
        self.create_treeview_section()

    def configure_treeview_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", background="#131313", foreground="#fafafa", font=("Arial", 12, "bold"), relief="flat")
        style.configure("Treeview", background="#131313", foreground="#fafafa", fieldbackground="#131313", borderwidth=0, relief="flat")
        style.map("Treeview.Heading", background=[("selected", "#252525"), ("active", "#252525")])

    def create_widgets_section(self):
        ctk.CTkLabel(self, text=app.translator.translate("LABEL_WIDGETS_TEXT")).grid(row=0, column=0, padx=self.PADDING, pady=self.PADDING, sticky="w")
        for i, widget in enumerate(widgets):
            self.create_widget_button(widget, i + 1, True)
        #self.create_widget_button(app.translator.translate("IMPORT_WIDGET_BUTTON"), i + 1)

    def import_custom_widget(self):
        widget=load_classes_from_file(filedialog.askopenfilename(
            title=translator.translate("FILE_DIALOG_SELECT_FILE"),
            filetypes=[(translator.get("filedialog.file_type"), "*.py"), ("Todos los archivos", "*.*")]
        ))
        app.cross_update_text_info(app.translator.translate_with_vars("USER_WIDGET_DETAILS", {"widget": widget}))
        app.virtual_window._extracted_from_create_and_place_widget_5(widget[0](self.virtual_window), 100, 100)

    def check_widget(self, widget:object):
        if widget == "Importar": return self.import_custom_widget
        else: return lambda w=widget: self.add_widget(w)

    def create_widget_button(self, widget:object, row:int, h:str = None):
        """Crea un botón para cada widget y lo agrega a la sección de widgets."""
        dic_help = widgets_info.get(app.translator.current_language)
        btn = ctk.CTkButton(
            self,
            text=widget,
            command=self.check_widget(widget),
            **BUTTON_STYLE
        )
        btn.grid(row=row, column=0, padx=self.PADDING, pady=2, sticky="ew")
        if h:
            CTkToolTip(btn, dic_help[row-1])
        self.buttons[widget] = btn

    def disable_buttons(self):
        """Desactiva todos los botones creados."""
        for btn in self.buttons.values():
            btn.configure(state="disabled")
            
    def enable_buttons(self):
        """Activa todos los botones creados."""
        for btn in self.buttons.values():
            btn.configure(state="normal")

    def create_treeview_section(self):
        ctk.CTkLabel(self, text=app.translator.translate("LABEL_SCHEME_TEXT")).grid(row=len(widgets) + 1, column=0, padx=self.PADDING, pady=self.PADDING, sticky="w")
        self.tree = ttk.Treeview(self, selectmode="browse", show="tree")
        self.tree.grid(row=len(widgets) + 2, column=0, padx=self.PADDING, pady=self.PADDING, sticky="nsew")
        self.tree.column("#0", width=self.TREEVIEW_WIDTH, stretch=True)
        self.tree.heading("#0", text="Widgets")

    def add_widget(self, widget:object):
        """Añade un widget a la ventana virtual y actualiza el esquema del TreeView."""
        self.virtual_window.add_widget(widget)
        self.update_treeview()

    def detect_hierarchy(self, parent_widget:object=None):
        """Detecta automáticamente la jerarquía de widgets dentro de la ventana virtual."""
        hierarchy = []
        container = parent_widget or self.virtual_window

        for child in container.winfo_children():
            hierarchy.append((child, parent_widget))
            hierarchy.extend(self.detect_hierarchy(child))

        return hierarchy

    def update_treeview(self):
        """Actualiza el esquema del TreeView basado en la jerarquía detectada automáticamente."""
        widget_hierarchy = self.detect_hierarchy()
        update_treeview(self.tree, widget_hierarchy, self.widget_tree)

    def insert_widget_into_tree(self, widget:object, parent_widget:object):
        widget_name = widget._name if hasattr(widget, "_name") else widget.__class__.__name__
        widget_id = id(widget)

        if parent_widget:
            parent_id = id(parent_widget)
            parent_tree_id = self.widget_tree.get(parent_id)
            tree_id = self.tree.insert(parent_tree_id, "end", text=widget_name)
        else:
            tree_id = self.tree.insert("", "end", text=widget_name)

        self.widget_tree[widget_id] = tree_id

class Toolbar(ctk.CTkFrame):
    PROGRESS_BAR_HIDE_DELAY = 3000

    def __init__(self, parent, virtual_window, rightbar, initialize_on_import=False):
        super().__init__(parent, height=40, fg_color="#222222") #Anterior #333333
        self.virtual_window = virtual_window
        self.right_bar = rightbar
        
        self.config_window = None
        
        self.pack_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        self.create_buttons()
        self.create_info_label()
        self.create_progress_bar()

        self.initialize_on_import = initialize_on_import

    def apply_configs(self, language:str, theme:str):
        app.switch_language(language)

    def create_config_widgets(self, config_window):
        """Crea los widgets de configuración en una ventana con scrollbar."""
        #config_window.resizable(False, False)
        def apply_config():
            """Aplica y guarda los cambios de configuración."""
            app.config_manager.set("General", "theme", theme.get())
            app.config_manager.set("Export", "format", export_format.get())
            app.config_manager.set("Export", "include_comments", include_comments.get())
            app.config_manager.set("Export", "resizable", is_resizable.get())

            if str(app.config_manager.get("General", "language")) != str(language.get()):
                app.config_manager.set("General", "language", language.get()) # Se aplica aqui el cambio de idioma para actualizar bien el cambio
                msg = CTkMessagebox(
                    title="Save", message=translator.get("messagebox.toolbar.apply_config.user_config_saved_confirmation"),
                    icon="question", option_1=translator.get("messagebox.toolbar.apply_config.negative_button")
                    , option_2=translator.get("messagebox.toolbar.apply_config.neutral_button")
                    , option_3=translator.get("messagebox.toolbar.apply_config.afirmative_button")
                )
                if msg.get() == translator.get("messagebox.toolbar.apply_config.afirmative_button"):
                    app.destroy()
            app.cross_update_text_info(app.translator.translate("USER_CONFIG_SAVED"))

        def select_value(widget, value:int):
            if value == 1:
                widget.select()
            else:
                widget.deselect()

        # ScrollableFrame
        scroll_frame = ctk.CTkScrollableFrame(config_window, width=380, height=280)
        scroll_frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(scroll_frame, text=translator.get("toolbar.configuration_section.label_languaje")).pack(anchor="center", padx=20, pady=5)

        # Configuración de idioma y tema
        ctk.CTkLabel(scroll_frame, text=translator.get("toolbar.configuration_section.label_languaje")).pack(anchor="w", padx=20, pady=5)
        language = ctk.CTkComboBox(scroll_frame, values=['es', 'en'], state='readonly')
        language.pack(fill="x", padx=20, pady=5)
        language.set(app.config_manager.get("General", "language"))

        ttk.Separator(scroll_frame, orient="horizontal").pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(scroll_frame, text=translator.get("toolbar.configuration_section.label_personalization")).pack(anchor="center", padx=20, pady=5)

        ctk.CTkLabel(scroll_frame, text=translator.get("toolbar.configuration_section.label_theme")).pack(anchor="w", padx=20, pady=5)
        theme = ctk.CTkComboBox(scroll_frame, values=['dark-blue', 'light'], state='readonly')
        theme.pack(fill="x", padx=20, pady=5)
        theme.set(app.config_manager.get("General", "theme"))

        ttk.Separator(scroll_frame, orient="horizontal").pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(scroll_frame, text=translator.get("toolbar.configuration_section.label_exportation")).pack(anchor="center", padx=20, pady=5)

        # Selector de formato de exportación
        ctk.CTkLabel(scroll_frame, text=translator.get("toolbar.configuration_section.label_format_exportation")).pack(anchor="w", padx=20, pady=5)
        export_format = ctk.CTkComboBox(scroll_frame, values=['py', 'json'], state='readonly')
        export_format.pack(fill="x", padx=20, pady=5)
        export_format.set(app.config_manager.get("Export", "format", fallback='py'))

        # Checkbox para definir el resizable
        is_resizable = ctk.CTkCheckBox(scroll_frame, text=app.translator.translate("RESIZABLE"))
        is_resizable.pack(anchor="w", padx=20, pady=5)
        select_value(is_resizable, app.config_manager.get("Export", "resizable"))

        # Checkbox para incluir comentarios
        include_comments = ctk.CTkCheckBox(scroll_frame, text=translator.get("toolbar.configuration_section.label_allow_comments"))
        include_comments.pack(anchor="w", padx=20, pady=5)
        select_value(include_comments, app.config_manager.get("Export", "include_comments"))

        # Botón para aplicar cambios
        ctk.CTkButton(scroll_frame, text=translator.get("toolbar.configuration_section.button_apply_changes")
                      , command=apply_config).pack(pady=40)

        # Botón para restaurar valores por defecto
        def reset_defaults():
            language.set('es')
            theme.set('dark-blue')
            export_format.set('py')
            include_comments.deselect()
            apply_config()

        ctk.CTkButton(scroll_frame, text=translator.get("toolbar.configuration_section.button_reset_config")
                      , command=reset_defaults).pack()

    def open_config_window(self):
        """Abre la ventana de configuraciones si no está ya abierta."""
        if self.config_window is None or not self.config_window.winfo_exists():
            self.config_window = ctk.CTkToplevel(self)
            self.config_window.title(translator.get("toolbar.configuration_section.window_title"))
            self.config_window.geometry("400x300")
            self.config_window.after(100, self.config_window.lift)
            self.create_config_widgets(self.config_window)
            
            label = ctk.CTkLabel(self.config_window, text=translator.get("toolbar.configuration_section.window_title"))
            label.pack(pady=10)
        else:
            self.config_window.lift()
    
    def create_buttons(self):
        """Crea y empaqueta los botones de la barra de herramientas."""
        self.create_button("Code preview", self.change_view, side="right")
        self.create_button(app.translator.translate("CONSOLE_BUTTON_TEXT"), self.open_console, side="right")
        self.create_button("Theme Manager", self.open_theme_manager, side="right") # Nuevo botón

    def open_theme_manager(self):
        """Abre el gestor de temas."""
        if not hasattr(self, 'theme_window'):
            self.theme_window = ctk.CTkToplevel(self)
            self.theme_window.title("Theme Manager")
            self.theme_window.geometry("500x700")
            self.theme_manager = ThemeManager(self.theme_window, app)
            self.theme_manager.pack(fill="both", expand=True)
        else:
            self.theme_window.lift()
    
    def open_console(self):
        """Abre la consola de la aplicación."""
        app.open_console()
    
    def change_view(self):
        """Cambia el modo de visualización del código."""
        
        app.view_code()
    
    def create_button(self, text:str, command:any, side:str):
        """Método auxiliar para crear un botón."""
        button = ctk.CTkButton(self, text=text, command=command, **BUTTON_STYLE)
        button.pack(pady=5, padx=5, side=side)

    def create_info_label(self):
        """Crea y empaqueta la etiqueta de información."""
        self.info_label = ctk.CTkLabel(self, text="Ok")
        self.info_label.pack(pady=5, padx=5, side="left")

    def create_progress_bar(self):
        """Crea y empaqueta la barra de progreso."""
        self.progress = ctk.CTkProgressBar(self)
        self.progress.pack(pady=5, padx=5, side="left")
        self.progress.set(0)
        self.progress.pack_forget()

    def progress_set_value(self, value:float):
        """Establezca el valor de la barra de progreso y administre su visibilidad."""
        self.progress.set(value)
        if value < 1.0:
            self.progress.pack(pady=5, padx=5, side="left")
        else:
            self.after(self.PROGRESS_BAR_HIDE_DELAY, self.hide_progress_bar)

    def hide_progress_bar(self):
        """Oculta la barra de progreso si está completa."""
        if self.progress.get() == 1.0:
            self.progress.pack_forget()

    def export_to_file(self):
        """Exporte el contenido de la ventana virtual a un archivo Python."""
        if file_path := filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[(translator.translate("FILE_DIALOG_ARCHIVE"), "*.py")],
            title=translator.translate("FILE_DIALOG_SAVE_AS_TITLE"),
        ):
            self.virtual_window.export_to_file(file_path)

    def import_from_file(self):
        """Importe contenido desde un archivo Python a la ventana virtual."""
        if file_path := filedialog.askopenfilename(
            filetypes=[(translator.translate("FILE_DIALOG_ARCHIVE"), "*.py")], title="Abrir archivo"
        ):
            self.virtual_window.import_from_file(file_path)
            self.right_bar.update_treeview()

class App(ctk.CTk):
    """Main application class for CustomDesigner."""
    
    # Class constants
    DEFAULT_HEIGHT = 500
    DEFAULT_WIDTH = 800
    
    def __init__(self):
        super().__init__()
        self._initialize_core_components()
        self._setup_application_config()
        self._initialize_ui()
        
    #TEST
    def reset_window(self):
        """Reset the window to its default state."""
        # Delete all widgets from virtual window
        for widget in self.winfo_children():
            widget.destroy()
            
        # Reset window to default size
        self.configure(
            width=self.DEFAULT_WIDTH,
            height=self.DEFAULT_HEIGHT
        )
        self._initialize_ui()

    # =====================================
    # INITIALIZATION METHODS
    # =====================================
    def _initialize_core_components(self):
        self.config_manager = ConfigManager()
        self.translator = translator
        self.command_history = []
        
        # Application state
        self.import_proyect = False
        self.use_scene_manager = False
        
    def _setup_application_config(self):
        """Configure application window and appearance."""
        self.title("CustomDesigner")
        self.geometry("1000x600")
        self.resizable(False, False)
        ctk.set_appearance_mode(self.config_manager.get("General", "theme"))
        ctk.set_default_color_theme("dark-blue")
        
    def _initialize_ui(self):
        """Initialize the complete UI structure."""
        self._setup_fonts_and_styles()
        self._setup_initial_layout()
        self._create_initial_interface()

    def _setup_fonts_and_styles(self):
        """Define fonts and styling dictionaries."""
        self.TITLE_FONT = ctk.CTkFont(family="Helvetica", size=36, weight="bold")
        self.SUBTITLE_FONT = ctk.CTkFont(family="Helvetica", size=18)
        self.LABEL_FONT = ctk.CTkFont(family="Helvetica", size=14)

        self.ENTRY_STYLE = {
            'fg_color': 'transparent',
            'border_width': 2,
            'border_color': '#1F6AA5',
            'text_color': ('gray10', 'gray90'),
            'width': 140,
            'height': 35,
            'corner_radius': 8,
            'font': self.LABEL_FONT
        }
        
        self.CHECKBOX_STYLE = {
            'fg_color': '#1F6AA5',
            'text_color': ('gray10', 'gray90'),
            'hover_color': '#2980B9',
            'border_width': 2,
            'border_color': '#1F6AA5',
            'checkmark_color': ('gray90', 'gray10'),
            'corner_radius': 5,
            'font': self.LABEL_FONT
        }

    def _setup_initial_layout(self):
        """Configure initial grid layout."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _create_initial_interface(self):
        """Create the initial project setup interface."""
        self._create_virtual_window_container()
        self._create_project_setup_ui()

    # =====================================
    # INITIAL PROJECT SETUP UI
    # =====================================
    
    def _create_virtual_window_container(self):
        """Create the main container for the initial interface."""
        self.virtual_window = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.virtual_window.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        self.virtual_window.grid_columnconfigure((0, 1), weight=1)
        self.virtual_window.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

    def _create_project_setup_ui(self):
        """Create all UI elements for project setup."""
        self._create_title_section()
        self._create_configuration_section()
        self._create_input_fields()
        self._create_action_buttons()

    def _create_title_section(self):
        """Create the main title label."""
        title_label = ctk.CTkLabel(
            self.virtual_window, 
            text=self.translator.translate("NEW_PROYECT"), 
            font=self.TITLE_FONT, 
            text_color=('gray10', 'gray90')
        )
        title_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=30, pady=(30, 10))

    def _create_configuration_section(self):
        """Create the window configuration section label."""
        config_label = ctk.CTkLabel(
            self.virtual_window, 
            text=self.translator.translate("WINDOW_CONFIG"), 
            font=self.SUBTITLE_FONT, 
            text_color=('gray20', 'gray80')
        )
        config_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=30, pady=(10, 20))

    def _create_input_fields(self):
        """Create input fields for window dimensions."""
        validate_command = self.register(validate_input)

        self.hvar = ctk.StringVar(value=str(self.DEFAULT_HEIGHT))
        self._create_labeled_entry("HEIGHT", self.hvar, 2, validate_command)

        self.wvar = ctk.StringVar(value=str(self.DEFAULT_WIDTH))
        self._create_labeled_entry("WIDTH", self.wvar, 3, validate_command)

    def _create_labeled_entry(self, label_key, text_var, row, validate_command):
        """Create a label and entry pair."""
        label_text = self.translator.translate(label_key)
        
        label = ctk.CTkLabel(
            self.virtual_window, 
            text=label_text, 
            font=self.LABEL_FONT, 
            text_color=('gray10', 'gray90')
        )
        label.grid(row=row, column=0, sticky="e", padx=(20, 10), pady=10)
        
        entry = ctk.CTkEntry(
            self.virtual_window, 
            textvariable=text_var, 
            validate="key", 
            validatecommand=(validate_command, "%P"), 
            placeholder_text=text_var.get(), 
            **self.ENTRY_STYLE
        )
        entry.grid(row=row, column=1, sticky="w", padx=(10, 30), pady=10)

    def _create_action_buttons(self):
        """Create the main action buttons."""
        create_btn = ctk.CTkButton(
            self.virtual_window, 
            text=self.translator.translate("CREATE_PROJECT"), 
            command=self.create_project, 
            font=self.LABEL_FONT, 
            **BUTTON_STYLE
        )
        create_btn.grid(row=8, column=0, columnspan=2, sticky="se", padx=30, pady=30)
        
        import_btn = ctk.CTkButton(
            self.virtual_window, 
            text=self.translator.translate("IMPORT_PROJECT"), 
            command=lambda: self.create_project(True), 
            font=self.LABEL_FONT, 
            **BUTTON_STYLE
        )
        import_btn.grid(row=8, column=4, columnspan=2, sticky="se", padx=30, pady=30)

    # =====================================
    # PROJECT CREATION AND TRANSITION
    # =====================================
    
    def create_project(self, import_proyect=False):
        """Handle project creation with specified dimensions."""
        self.import_proyect = import_proyect
        height = self.hvar.get()
        width = self.wvar.get()
        
        app.cross_update_text_info(
            self.translator.translate_with_vars(
                "USER_PROYECT_DETAILS", 
                {"height": height, "width": width}
            )
        )
        
        self._transition_to_main_ui(height, width)

    def _transition_to_main_ui(self, height, width):
        """Transition from setup to main UI."""
        # Convert integers to strings if needed
        height = str(height) if isinstance(height, int) else height
        width = str(width) if isinstance(width, int) else width
        
        if not (height.isdigit() and width.isdigit()):
            logging.warning("Altura o anchura no válidas.")
            return
            
        self._cleanup_initial_interface()
        self._create_main_ui(int(height), int(width))
        self._setup_debug_features()

    def _cleanup_initial_interface(self):
        """Clean up the initial project setup interface."""
        for widget in self.virtual_window.winfo_children():
            widget.destroy()
        self.virtual_window.destroy()

    # =====================================
    # MAIN UI CREATION
    # =====================================
    
    def _create_main_ui(self, vw_height, vw_width):
        """Create and configure the main application UI."""
        self._setup_main_layout()
        self._create_main_components(vw_height, vw_width)  # Create toolbar first
        self._create_menu_system()  # Create menu system after toolbar
        self._handle_project_import()
        self._finalize_main_ui()

    def _setup_main_layout(self):
        """Configure the main window layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.resizable(True, True)

    def _create_menu_system(self):
        """Create the menu bar and dropdown system."""
        self._create_menu_container()
        self._create_menu_bar()
        self._setup_menu_dropdown()

    def _create_menu_container(self):
        """Create container for the menu bar."""
        self.menu_container = ctk.CTkFrame(self, height=25)
        self.menu_container.grid(row=0, column=0, columnspan=4, sticky="ew")
        self.menu_container.grid_propagate(False)

    def _create_menu_bar(self):
        """Create the main menu bar."""
        self.menu_bar = CTkMenuBar(
            self.menu_container,
            height=20,
            bg_color="#1a1a1a",
            padx=0,
            pady=0
        )
        self.menu_button = self.menu_bar.add_cascade(text=translator.translate("MENU_BAR_MENU_TITLE"))
        self.tool_button = self.menu_bar.add_cascade(text=translator.translate("MENU_BAR_TOOL_TITLE"))

    def _setup_menu_dropdown(self):
        """Setup the dropdown menu with options."""
        self.menu_button_drop = CustomDropdownMenu(
            widget=self.menu_button,
            master=self,
            width=150,
            fg_color="#2b2b2b",
            hover_color="#1f1f1f",
            corner_radius=8,
            border_width=1,
            border_color="grey30"
        )
        self.tool_button_drop = CustomDropdownMenu(
            widget=self.tool_button,
            master=self,
            width=150,
            fg_color="#2b2b2b",
            hover_color="#1f1f1f",
            corner_radius=8,
            border_width=1,
            border_color="grey30"
        )
        self._populate_menu_options()
        self._populate_tools_options()

    def _populate_menu_options(self):
        """Add options to the dropdown menu."""
        menu_options = [
            (translator.get("project.NEW_PROYECT"), self.reset_window),
            "separator",
            (translator.translate("TOOL_BUTTON_EXPORT"), self.toolbar.export_to_file),
            (translator.translate("TOOL_BUTTON_CONFIG"), self.toolbar.open_config_window),
            "separator",
            (translator.get("menubar.exit_option"), self.quit)
        ]
        
        for option in menu_options:
            if option == "separator":
                self.menu_button_drop.add_separator()
            else:
                text, command = option
                self.menu_button_drop.add_option(text, command=command)
    
    def _populate_tools_options(self):
        """Create the tools dropdown menu with options."""
        tools_options = [
            (translator.translate("CONSOLE_BUTTON_TEXT"), self.toolbar.open_console),
            "separator",
            
        ]
        for option in tools_options:
            if option == "separator":
                self.tool_button_drop.add_separator()
            else:
                text, command = option
                self.tool_button_drop.add_option(text, command=command)
    def _create_main_components(self, vw_height, vw_width):
        """Create the main UI components."""
        self._create_main_frame()
        self._create_sidebars()
        self._create_central_workspace(vw_height, vw_width)
        self._create_toolbar()

    def _create_main_frame(self):
        """Create the main container frame."""
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, columnspan=4, sticky="nsew")
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

    def _create_sidebars(self):
        """Create left and right sidebars."""
        self.left_sidebar = LeftSidebar(self.main_frame)
        self.left_sidebar.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    def _create_central_workspace(self, vw_height, vw_width):
        """Create the central canvas workspace."""
        self._create_central_frame()
        self._create_canvas_with_scrollbars()
        self._create_virtual_window(vw_height, vw_width)
        self._create_right_sidebar()

    def _create_central_frame(self):
        """Create the central frame container."""
        self.central_frame = ctk.CTkFrame(self.main_frame)
        self.central_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.central_frame.grid_columnconfigure(0, weight=1)
        self.central_frame.grid_rowconfigure(0, weight=1)

    def _create_canvas_with_scrollbars(self):
        """Create canvas with horizontal and vertical scrollbars."""
        self.central_canvas = tk.Canvas(self.central_frame, bg="black")
        self.central_canvas.grid(row=0, column=0, sticky="nsew")
        
        self._create_scrollbars()
        self._configure_canvas_scrolling()

    def _create_scrollbars(self):
        """Create horizontal and vertical scrollbars."""
        self.h_scrollbar = ctk.CTkScrollbar(
            self.central_frame,
            orientation="horizontal",
            command=self.central_canvas.xview
        )
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.v_scrollbar = ctk.CTkScrollbar(
            self.central_frame,
            orientation="vertical",
            command=self.central_canvas.yview
        )
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")

    def _configure_canvas_scrolling(self):
        """Configure canvas scrolling behavior."""
        self.central_canvas.configure(
            xscrollcommand=self.h_scrollbar.set,
            yscrollcommand=self.v_scrollbar.set
        )
        self.central_canvas.bind('<Configure>', self._update_scrollbars)

    def _create_virtual_window(self, vw_height, vw_width):
        """Create the virtual window for design."""
        self.virtual_window = VirtualWindow(
            self.central_canvas,
            self.left_sidebar,
            self,
            width=vw_width,
            height=vw_height
        )
        
        self.virtual_window_id = self.central_canvas.create_window(
            50, 50,
            anchor="nw",
            window=self.virtual_window
        )

    def _create_right_sidebar(self):
        """Create the right sidebar."""
        self.right_sidebar = RightSidebar(self.main_frame, self.virtual_window)
        self.right_sidebar.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

    def _create_toolbar(self):
        """Create the bottom toolbar."""
        self.toolbar = Toolbar(self, self.virtual_window, self.right_sidebar, self.import_proyect)
        self.toolbar.grid(row=2, column=0, columnspan=4, sticky="ew")

    def _handle_project_import(self):
        """Handle project import if requested."""
        if self.import_proyect:
            if file_path := filedialog.askopenfilename(
                filetypes=[
                    (
                        self.translator.translate("FILE_DIALOG_JSON_ARCHIVE"),
                        "*.json",
                    )
                ],
                title="Abrir archivo",
            ):
                self.virtual_window.import_from_json(file_path)

    def _finalize_main_ui(self):
        """Finalize the main UI setup."""
        self.central_canvas.configure(scrollregion=self.central_canvas.bbox("all"))

    def _setup_debug_features(self):
        """Setup debug features if enabled."""
        if TOOLTIP_INFO_WIDGET:
            self.toolbar.create_button(
                "Debug Grid", 
                self.display_grid_debug,
                "right"
            )
        self.display_tooltip()

    # =====================================
    # UI UPDATE AND MANAGEMENT
    # =====================================
    
    def _update_scrollbars(self, event=None):
        """Update scrollbar visibility based on content size."""
        bbox = self.central_canvas.bbox("all")
        if not bbox:
            return
            
        canvas_width = self.central_canvas.winfo_width()
        canvas_height = self.central_canvas.winfo_height()

        # Show/hide horizontal scrollbar
        if bbox[2] - bbox[0] > canvas_width:
            self.h_scrollbar.grid()
        else:
            self.h_scrollbar.grid_remove()

        # Show/hide vertical scrollbar
        if bbox[3] - bbox[1] > canvas_height:
            self.v_scrollbar.grid()
        else:
            self.v_scrollbar.grid_remove()

    def switch_language(self, language):
        """Switch application language."""
        try:
            self.translator.set_language(language)
            self.refresh_ui()
        except ValueError as e:
            app.cross_update_text_info(str(e))

    def refresh_ui(self):
        """Refresh UI text after language change."""
        components = [self.toolbar, self.left_sidebar, self.right_sidebar]
        
        for component in components:
            self._refresh_component_text(component)

    def _refresh_component_text(self, component):
        """Refresh text for a specific UI component."""
        for widget in component.winfo_children():
            if isinstance(widget, (ctk.CTkLabel, ctk.CTkButton)):
                try:
                    current_text = widget.cget('text')
                    key = self.translator.find_key_by_value(current_text)
                    new_text = self.translator.translate(key)
                    widget.configure(text=new_text)
                    logging.debug(f"Updated {widget.__class__.__name__}: {new_text}")
                except Exception:
                    continue

    # =====================================
    # CODE VIEW AND EDITING
    # =====================================
    
    def view_code(self):
        """Toggle between design view and code view."""
        if self.virtual_window.toggle_visibility():
            self._enter_code_view()
        else:
            self._exit_code_view()

    def _enter_code_view(self):
        """Enter code editing mode."""
        self.virtual_window.replace()
        self._create_code_editor()
        self.right_sidebar.disable_buttons()

    def _create_code_editor(self):
        """Create the code editor component."""
        self.code = CTkCodeBox(
            self.central_canvas, 
            height=500, 
            width=800, 
            language='python'
        )
        self.code.place(x=50, y=50)
        
        code_content = "\n".join(self.virtual_window.previsualize_code())
        self.code.insert('1.0', code_content)
        self.code.bind("<KeyRelease>", self.update_virtual_window)

    def _exit_code_view(self):
        """Exit code editing mode."""
        self.right_sidebar.enable_buttons()
        if hasattr(self, 'code'):
            self.code.destroy()

    def update_virtual_window(self, event):
        """Update virtual window with current code content."""
        new_code = self.code.get('1.0', 'end-1c')
        self.virtual_window.import_from_codebox(new_code)
        logging.debug(self.virtual_window.widgets)

    # =====================================
    # WIDGET MANAGEMENT
    # =====================================
    
    def inter_add_widget(self, widget):
        """Add a widget to the virtual window with its properties."""
        kwargs_dict = self._extract_widget_properties(widget)
        self.virtual_window.paste_widget(widget, **kwargs_dict)

    def _extract_widget_properties(self, widget):
        """Extract properties from a widget for copying."""
        kwargs_dict = {}
        widget_class = widget.__class__.__name__
        
        if widget_class in global_properties:
            for prop in global_properties[widget_class]:
                try:
                    kwargs_dict[prop] = widget.cget(prop)
                except Exception:
                    kwargs_dict[prop] = None
                    
        return kwargs_dict

    # =====================================
    # CROSS-COMPONENT COMMUNICATION
    # =====================================
    
    def cross_update_treeview(self):
        """Update the treeview in right sidebar."""
        self.right_sidebar.update_treeview()

    def cross_update_progressbar(self, val):
        """Update the progress bar value."""
        self.toolbar.progress_set_value(val)

    def cross_update_text_info(self, val):
        """Update the info text with auto-reset."""
        try:
            self.toolbar.info_label.configure(text=val)
            self.after(3000, lambda: self.toolbar.info_label.configure(text='Ok.'))
        except AttributeError:
            print("Toolbar not initialized or info_label not found.")
    # =====================================
    # CONSOLE AND COMMAND SYSTEM
    # =====================================
    
    def open_console(self):
        """Open the interactive console window."""
        console = self._create_console_window()
        console_state = self._initialize_console_state()
        
        output_textbox = self._create_console_output(console)
        input_frame, input_entry = self._create_console_input(console)
        
        self._setup_console_commands(console_state, output_textbox, input_entry)
        self._bind_console_events(input_entry, console_state)

    def _create_console_window(self):
        """Create the console window."""
        console = ctk.CTkToplevel(self)
        console.title(self.translator.translate("CONSOLE_BUTTON_TEXT"))
        console.geometry("600x400")
        console.after(100, console.lift)
        return console

    def _initialize_console_state(self):
        """Initialize console state variables."""
        return {
            'command_history': [],
            'history_index': -1,
            'custom_command_active': False
        }

    def _create_console_output(self, console):
        """Create console output textbox."""
        output_textbox = ctk.CTkTextbox(console, width=580, height=300, wrap="word")
        output_textbox.pack(pady=10, padx=10)
        output_textbox.configure(state="disabled")
        return output_textbox

    def _create_console_input(self, console):
        """Create console input frame and entry."""
        input_frame = ctk.CTkFrame(console)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        input_entry = ctk.CTkEntry(input_frame, width=480)
        input_entry.pack(side="left", padx=(0, 5), fill="x", expand=True)
        
        execute_button = ctk.CTkButton(
            input_frame, 
            text=self.translator.translate("CONSOLE_BUTTON_RUN")
        )
        execute_button.pack(side="right")
        
        return input_frame, input_entry

    def _setup_console_commands(self, state, output_textbox, input_entry):
        """Setup console command execution."""
        def execute_command():
            self._execute_console_command(state, output_textbox, input_entry)
        
        # Bind execute command to button and entry
        input_entry.bind("<Return>", lambda event: execute_command())
        
        # Get execute button and bind command
        execute_button = input_entry.master.winfo_children()[-1]
        execute_button.configure(command=execute_command)

    def _execute_console_command(self, state, output_textbox, input_entry):
        """Execute a console command."""
        output_textbox.configure(state="normal")
        command = input_entry.get()
        
        if not command.strip():
            return
            
        try:
            self._run_command(command, output_textbox, state)
            state['command_history'].append(command)
        except Exception as e:
            output_textbox.insert(ctk.END, f"> {command}\nError: {str(e)}\n")
        finally:
            input_entry.delete(0, ctk.END)
            output_textbox.configure(state="disabled")

    def _run_command(self, command, output_textbox, state):
        """Run a specific command in the console."""
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
        
        try:
            if command.startswith("$"):
                state['custom_command_active'] = True
                self._handle_custom_command(command[1:])
            else:
                state['custom_command_active'] = False
                result = eval(command)
                if result is not None:
                    print(result)
            
            output = sys.stdout.getvalue()
            error = sys.stderr.getvalue()
            output_textbox.insert(ctk.END, f"> {command}\n{output}{error}\n")
            output_textbox.see(ctk.END)
            
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr

    def _handle_custom_command(self, cmd):
        """Handle custom console commands."""
        parts = cmd.split(maxsplit=1)
        command = parts[0]
        args = parts[1].split() if len(parts) > 1 else []

        if command not in COMMAND_MAP:
            print(f"Unknown command: {cmd}")
            return

        try:
            self._execute_mapped_command(command, args)
        except TypeError:
            print(f"Usage error: Check 'help' for correct usage of '{command}'")

    def _execute_mapped_command(self, command, args):
        """Execute a mapped custom command."""
        no_arg_commands = ["clear", "exit"]
        app_only_commands = [
            "list_widgets", "show_config", "undo", "redo", 
            "debug_widgets", "clean_widgets", "debug_undo_stack",
            "debug_redo_stack", "export_img", "inspect_events"
        ]
        app_with_args_commands = [
            "change_theme", "change_language", "save_project", 
            "load_project", "show_widget_info", "run_code", 
            "export_json", "import_json", "exec"
        ]

        if command in no_arg_commands:
            target = self if command == "exit" else None
            COMMAND_MAP[command](target)
        elif command in app_only_commands:
            COMMAND_MAP[command](self)
        elif command in app_with_args_commands:
            COMMAND_MAP[command](self, args)
        else:
            COMMAND_MAP[command]([])

    def _bind_console_events(self, input_entry, state):
        """Bind keyboard events for console."""
        def browse_history(direction):
            self._browse_command_history(input_entry, state, direction)
        
        def check_custom_command(event):
            text = input_entry.get()
            state['custom_command_active'] = text.startswith("$")

        input_entry.bind("<Up>", lambda event: browse_history(-1))
        input_entry.bind("<Down>", lambda event: browse_history(1))
        input_entry.bind("<KeyRelease>", check_custom_command)

    def _browse_command_history(self, input_entry, state, direction):
        """Browse through command history."""
        if not state['command_history']:
            return
            
        state['history_index'] += direction
        
        if state['history_index'] < 0:
            state['history_index'] = 0
        elif state['history_index'] >= len(state['command_history']):
            state['history_index'] = len(state['command_history'])
            input_entry.delete(0, ctk.END)
            return
            
        input_entry.delete(0, ctk.END)
        input_entry.insert(0, state['command_history'][state['history_index']])

    # =====================================
    # DEBUG AND TESTING FEATURES
    # =====================================
    
    def mark_widget_with_color(self, widget, color='red'):
        """Mark a widget with a specific color for debugging."""
        if not hasattr(widget, "configure"):
            logging.warning("Widget doesn't have 'configure' method.")
            return
            
        color_default = widget.cget("fg_color")
        widget.configure(fg_color=color)
        
        if hasattr(self, 'widget_marked_color') and self.widget_marked_color:
            self.widget_marked_color.configure(fg_color=color_default)
        self.widget_marked_color = widget

    def display_tooltip(self):
        """Display debug tooltips for main UI components."""
        if not TOOLTIP_INFO_WIDGET:
            return
            
        main_widgets = [
            self.main_frame, self.toolbar, self.left_sidebar, 
            self.right_sidebar, self.virtual_window, self.menu_bar
        ]
        
        for widget in main_widgets:
            tooltip_text = self._generate_tooltip_text(widget)
            tooltip = CTkToolTip(
                widget,
                message=tooltip_text,
                alpha=0.9,
                font=("Consolas", 11),
                delay=0.5
            )
            tooltip.show()

    def _generate_tooltip_text(self, widget):
        """Generate tooltip text for a widget."""
        tooltip_text = f"Widget: {widget.__class__.__name__}\n"
        tooltip_text += f"Position: ({widget.winfo_x()}, {widget.winfo_y()})\n"
        tooltip_text += f"Size: {widget.winfo_width()}x{widget.winfo_height()}\n"
        
        try:
            tooltip_text += f"Grid Info: {widget.grid_info()}\n"
        except Exception:
            tooltip_text += "Grid Info: N/A\n"

        widget_class = widget.__class__.__name__
        if widget_class in global_properties:
            tooltip_text += "\nProperties:\n"
            for prop in global_properties[widget_class]:
                try:
                    value = widget.cget(prop)
                    tooltip_text += f"{prop}: {value}\n"
                except Exception:
                    continue

        child_count = len(widget.winfo_children())
        tooltip_text += f"\nChildren Count: {child_count}"
        
        return tooltip_text

    def display_grid_debug(self):
        """Display grid debugging visualization."""
        debug_canvas = self._create_debug_canvas()
        self._draw_grid_lines(debug_canvas)
        self._draw_widget_cells(debug_canvas)
        self._add_debug_close_button(debug_canvas)

    def _create_debug_canvas(self):
        """Create transparent canvas for grid debugging."""
        debug_canvas = tk.Canvas(
            self.main_frame,
            highlightthickness=0,
            bg='#000001'
        )
        debug_canvas.place(
            x=0, y=0,
            width=self.main_frame.winfo_width(),
            height=self.main_frame.winfo_height()
        )
        return debug_canvas

    def _draw_grid_lines(self, debug_canvas):
        """Draw grid lines on debug canvas."""
        GRID_COLOR = "#FF0000"
        
        rows = self.main_frame.grid_size()[1]
        cols = self.main_frame.grid_size()[0]
        
        cell_width = self.main_frame.winfo_width() / cols
        cell_height = self.main_frame.winfo_height() / rows

        # Draw horizontal lines
        for i in range(rows + 1):
            y = i * cell_height
            debug_canvas.create_line(
                0, y, self.main_frame.winfo_width(), y, 
                fill=GRID_COLOR, dash=(4, 2)
            )

        # Draw vertical lines
        for i in range(cols + 1):
            x = i * cell_width
            debug_canvas.create_line(
                x, 0, x, self.main_frame.winfo_height(), 
                fill=GRID_COLOR, dash=(4, 2)
            )

        return cell_width, cell_height

    def _draw_widget_cells(self, debug_canvas):
        """Draw widget cell information on debug canvas."""
        CELL_COLOR = "#00FF00"
        TEXT_COLOR = "#FFFFFF"

        cell_width, cell_height = self._calculate_cell_dimensions()

        for widget in self.main_frame.winfo_children():
            if not widget.winfo_viewable():
                continue

            if grid_info := widget.grid_info():
                self._draw_widget_cell(
                    debug_canvas, widget, grid_info, 
                    cell_width, cell_height, CELL_COLOR, TEXT_COLOR
                )

    def _calculate_cell_dimensions(self):
        """Calculate grid cell dimensions."""
        rows = self.main_frame.grid_size()[1]
        cols = self.main_frame.grid_size()[0]
        
        cell_width = self.main_frame.winfo_width() / cols
        cell_height = self.main_frame.winfo_height() / rows
        
        return cell_width, cell_height

    def _draw_widget_cell(self, debug_canvas, widget, grid_info, 
                         cell_width, cell_height, cell_color, text_color):
        """Draw individual widget cell on debug canvas."""
        row = grid_info['row']
        col = grid_info['column']
        rowspan = grid_info.get('rowspan', 1)
        colspan = grid_info.get('colspan', 1)

        # Calculate cell position
        x1 = col * cell_width
        y1 = row * cell_height
        x2 = x1 + (cell_width * colspan)
        y2 = y1 + (cell_height * rowspan)

        # Draw cell rectangle
        debug_canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=cell_color,
            width=2
        )

        # Add cell information text
        text = f"{widget.__class__.__name__}\n"
        text += f"({row},{col})\n"
        text += f"span:({rowspan},{colspan})"

        debug_canvas.create_text(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            text=text,
            fill=text_color,
            font=("Consolas", 8)
        )

    def _add_debug_close_button(self, debug_canvas):
        """Add close button to debug canvas."""
        close_btn = ctk.CTkButton(
            debug_canvas,
            text="Close Grid Debug",
            command=debug_canvas.destroy
        )
        close_btn.place(x=10, y=10)

    # =====================================
    # UTILITY METHODS
    # =====================================
    
    create_ui = _create_main_ui  # Alias for backward compatibility
    clear_virtual_window = _transition_to_main_ui  # Alias for backward compatibility
        
if __name__ == "__main__":
    app = App()
    app.mainloop()