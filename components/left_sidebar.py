import customtkinter as ctk
from core import *
from functions.sidebars_utils import clear_widgets, create_property_entries
from data.variable import *
from functions.generic import *
from functions.import_widget import *
import logging
class LeftSidebar(ctk.CTkScrollableFrame):
    PADDING = 5
    ROW_SCENE = 0

    def __init__(self, parent, app):
        self.widget_dict = {}
        self.app = app
        
        super().__init__(parent, width=200)
        self.grid_columnconfigure(0, weight=1)

        self.widget_config_scrollable = self.create_scrollable_frame()
        self.widget_config_label = self.create_label(self.widget_config_scrollable,
            self.app.translator.translate("CONFIG_LABEL_TEXT")
        )

        self.config_space = self.create_config_space()
        if self.app.use_scene_manager:
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
        frame (ctk.CTkScrollableFrame o ctk.CTkFrame): Un marco desplazable o un marco regular, dependiendo del valor de self.app.use_scene_manager.
        """
        frame = ctk.CTkScrollableFrame(self, width=200, height=350, fg_color='#292929') if self.app.use_scene_manager else ctk.CTkFrame(self, fg_color='#292929')
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
        self.app.cross_update_text_info(f"{self.app.translator.translate('USER_SHOW_WIDGET_CONFIG')} {widget_type}")
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

            self.app.cross_update_text_info(self.app.translator.translate_with_vars("USER_PROP_UPDATED", 
                        {"prop": prop, "widget": widget, "entry": new_value}))
            entry.configure(border_color="#565B5E")
            
        except Exception as e:
            self.app.cross_update_text_info(f"Error al actualizar '{prop}': {e}. Valor ingresado: {entry.get()}")
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
        self.app.cross_update_text_info(self.app.translator.translate_with_vars("USER_PROP_FONT_UPDATED", {"font_name": font_name, "font_size": font_size}))

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

        ctk.CTkLabel(self.config_space, text=self.app.translator.translate(arg0)).pack(
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
            self.app.cross_update_text_info(self.app.translator.translate("USER_VAR_UPDATED"))
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
            self.app.cross_update_text_info(self.app.translator.translate_with_vars("USER_POS_UPDATED", {"new_x": new_x, "new_y": new_y}))
        except ValueError:
            logging.warning("Posición inválida. Por favor, ingresa valores numéricos.")

    def create_action_buttons(self, widget:object): 
        """Create action buttons for the widget.

        Creates buttons for raising, lowering, and deleting the given widget, adding them to the configuration space.  Button labels are translated using the self.app translator.

        Args:
            widget: The widget for which to create action buttons.
        """

        actions = [ 
            (self.app.translator.translate("RIGHTBAR_BUTTON_UPLOAD_LAYER"), lambda: widget.lift()), 
            (self.app.translator.translate("RIGHTBAR_BUTTON_LOWER_LAYER"), lambda: widget.lower()), 
            (self.app.translator.translate("RIGHTBAR_BUTTON_DELETE_WIDGET"), lambda: self.delete_widget(widget)),
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
            self.app.virtual_window.delete_widget(widget)
            clear_widgets(self.config_space)
            self.app.cross_update_treeview()
        else:
            self.app.cross_update_text_info("No se puede borrar la virtual window")