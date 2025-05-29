import customtkinter as ctk
import tkinter.ttk as ttk
from tkinter import filedialog
from translations.translations import *
from objects.tooltip import CTkToolTip
from functions.sidebars_utils import update_treeview
from core import *
from functions.sidebars_utils import clear_widgets, create_property_entries
from data.variable import *
from functions.generic import *
from functions.import_widget import *
import logging
class RightSidebar(ctk.CTkScrollableFrame):
    TREEVIEW_WIDTH = 180
    PADDING = 5

    def __init__(self, parent, virtual_window, app):
        super().__init__(parent, width=200)
        self.app = app
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
        ctk.CTkLabel(self, text=self.app.translator.translate("LABEL_WIDGETS_TEXT")).grid(row=0, column=0, padx=self.PADDING, pady=self.PADDING, sticky="w")
        for i, widget in enumerate(widgets):
            self.create_widget_button(widget, i + 1, True)
        #self.create_widget_button(self.app.translator.translate("IMPORT_WIDGET_BUTTON"), i + 1)

    def import_custom_widget(self):
        widget=load_classes_from_file(filedialog.askopenfilename(
            title=translator.translate("FILE_DIALOG_SELECT_FILE"),
            filetypes=[(translator.get("filedialog.file_type"), "*.py"), ("Todos los archivos", "*.*")]
        ))
        self.app.cross_update_text_info(self.app.translator.translate_with_vars("USER_WIDGET_DETAILS", {"widget": widget}))
        self.app.virtual_window._extracted_from_create_and_place_widget_5(widget[0](self.virtual_window), 100, 100)

    def check_widget(self, widget:object):
        if widget == "Importar": return self.import_custom_widget
        else: return lambda w=widget: self.add_widget(w)

    def create_widget_button(self, widget:object, row:int, h:str = None):
        """Crea un botón para cada widget y lo agrega a la sección de widgets."""
        dic_help = widgets_info.get(self.app.translator.current_language)
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
        ctk.CTkLabel(self, text=self.app.translator.translate("LABEL_SCHEME_TEXT")).grid(row=len(widgets) + 1, column=0, padx=self.PADDING, pady=self.PADDING, sticky="w")
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