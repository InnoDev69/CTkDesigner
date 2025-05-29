import tkinter as tk
import tkinter.ttk as ttk
from data.commands import *
import customtkinter as ctk
from functions.sidebars_utils import *
from tkinter import filedialog
from functions.generic import *
from functions.import_widget import *
from CTkMessagebox import CTkMessagebox
from translations.translations import *
from functions.create_widget_animation import *
from objects.theme_manager import ThemeManager

class Toolbar(ctk.CTkFrame):
    PROGRESS_BAR_HIDE_DELAY = 3000

    def __init__(self, parent, virtual_window, rightbar, appi, initialize_on_import=False):
        super().__init__(parent, height=40, fg_color="#222222") #Anterior #333333
        self.virtual_window = virtual_window
        self.right_bar = rightbar
        global app
        app = appi
        
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