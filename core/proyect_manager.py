"""
ProjectManager - Gestiona el ciclo de vida completo de creación de proyectos
"""
import logging
from tkinter import filedialog
from typing import TYPE_CHECKING

from core.proyect import Project, ProjectSetupUI
from core.events import AppEvents

if TYPE_CHECKING:
    from main import App


class ProjectManager:
    """Gestor del ciclo de vida completo de proyectos.
    
    Orquesta la creación, transición, importación y reset de proyectos.
    También maneja la creación de toda la UI principal (sidebars, toolbar, etc).
    """

    def __init__(self, app: "App"):
        """Inicializa el gestor de proyectos.
        
        Args:
            app: Instancia de la aplicación principal (App).
        """
        self.app = app
        self.current_project: Project | None = None
        self.setup_ui: ProjectSetupUI | None = None

    def create_setup_ui(self) -> None:
        """Crea la interfaz de setup inicial."""
        self.setup_ui = ProjectSetupUI(self.app)
        self.setup_ui.create_initial_interface()

    def create_project(self, import_project: bool = False) -> None:
        """Inicia la creación de un nuevo proyecto.
        
        Args:
            import_project: Si es True, después se abrirá un diálogo de importación.
        """
        if not self.setup_ui:
            logging.warning("Setup UI no inicializado")
            return

        height = self.setup_ui.hvar.get() if self.setup_ui.hvar else "500"
        width = self.setup_ui.wvar.get() if self.setup_ui.wvar else "800"

        self._transition_to_main_ui(height, width, import_project)

    def _transition_to_main_ui(self, height: str, width: str, import_project: bool = False) -> None:
        """Transiciona de la pantalla de setup a la UI principal.
        
        Args:
            height: Altura del proyecto (como string).
            width: Anchura del proyecto (como string).
            import_project: Si es True, después importará un archivo.
        """
        height = str(height) if isinstance(height, int) else height
        width = str(width) if isinstance(width, int) else width

        if not (height.isdigit() and width.isdigit()):
            logging.warning("Altura o anchura no válidas: height=%s, width=%s", height, width)
            return

        # Crear proyecto
        self.current_project = Project(
            height=int(height),
            width=int(width),
            import_project=import_project,
        )

        # Limpiar UI de setup
        self._cleanup_setup_interface()

        # Crear UI principal
        self._create_main_ui(int(height), int(width))

        # Setup debug features
        self.app._setup_debug_features()

        # Emitir evento de que el proyecto está listo
        self.app.event_manager.emit(AppEvents.PROJECT_OPENED)

        logging.info(f"Proyecto creado: {self.current_project}")

    def _cleanup_setup_interface(self) -> None:
        """Limpia la interfaz de setup."""
        if self.setup_ui:
            self.setup_ui.cleanup()

    def _create_main_ui(self, vw_height: int, vw_width: int) -> None:
        """Crea toda la UI principal del proyecto.
        
        Args:
            vw_height: Altura del virtual window.
            vw_width: Anchura del virtual window.
        """
        self._setup_main_layout()
        self._create_main_components(vw_height, vw_width)
        self._create_menu_system()
        self._handle_project_import()
        self._finalize_main_ui()

    def _setup_main_layout(self) -> None:
        """Configura el layout principal."""
        self.app.grid_columnconfigure(0, weight=1)
        self.app.grid_rowconfigure(0, weight=0)
        self.app.grid_rowconfigure(1, weight=1)
        min_window_width = (
            self.app.LEFT_SIDEBAR_MIN_WIDTH
            + self.app.RIGHT_SIDEBAR_MIN_WIDTH
            + self.app.CENTER_MIN_WIDTH
            + 40
        )
        self.app.minsize(min_window_width, self.app.MAIN_MIN_HEIGHT)
        self.app.resizable(True, True)

    def _create_main_components(self, vw_height: int, vw_width: int) -> None:
        """Crea todos los componentes principales."""
        self._create_main_frame()
        self._create_left_sidebar()
        self._create_central_workspace(vw_height, vw_width)
        self._create_right_sidebar()
        self._create_toolbar()

    def _create_main_frame(self) -> None:
        """Crea el frame principal."""
        from components.left_sidebar import LeftSidebar
        import customtkinter as ctk

        self.app.main_frame = ctk.CTkFrame(self.app)
        self.app.main_frame.grid(row=1, column=0, columnspan=4, sticky="nsew")
        self.app.main_frame.grid_columnconfigure(0, weight=0, minsize=self.app.LEFT_SIDEBAR_MIN_WIDTH)
        self.app.main_frame.grid_columnconfigure(1, weight=1)
        self.app.main_frame.grid_columnconfigure(2, weight=0, minsize=self.app.RIGHT_SIDEBAR_MIN_WIDTH)
        self.app.main_frame.grid_rowconfigure(0, weight=1)

    def _create_left_sidebar(self) -> None:
        """Crea la sidebar izquierda."""
        from components.left_sidebar import LeftSidebar

        self.app.left_sidebar = LeftSidebar(self.app.main_frame, self.app)
        self.app.left_sidebar.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    def _create_central_workspace(self, vw_height: int, vw_width: int) -> None:
        """Crea el workspace central."""
        self._create_central_frame()
        self._create_canvas_with_scrollbars()
        self._create_virtual_window(vw_height, vw_width)

    def _create_central_frame(self) -> None:
        """Crea el frame central."""
        import customtkinter as ctk

        self.app.central_frame = ctk.CTkFrame(self.app.main_frame)
        self.app.central_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.app.central_frame.grid_columnconfigure(0, weight=1)
        self.app.central_frame.grid_rowconfigure(0, weight=1)

    def _create_canvas_with_scrollbars(self) -> None:
        """Crea el canvas con scrollbars."""
        import tkinter as tk

        self.app.central_canvas = tk.Canvas(self.app.central_frame, bg="black")
        self.app.central_canvas.grid(row=0, column=0, sticky="nsew")

        self.app._bind_canvas_pan_events()
        self._create_scrollbars()
        self._configure_canvas_scrolling()

    def _create_scrollbars(self) -> None:
        """Crea los scrollbars."""
        import customtkinter as ctk

        self.app.h_scrollbar = ctk.CTkScrollbar(
            self.app.central_frame,
            orientation="horizontal",
            command=self.app.central_canvas.xview,
        )
        self.app.h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.app.v_scrollbar = ctk.CTkScrollbar(
            self.app.central_frame,
            orientation="vertical",
            command=self.app.central_canvas.yview,
        )
        self.app.v_scrollbar.grid(row=0, column=1, sticky="ns")

    def _configure_canvas_scrolling(self) -> None:
        """Configura el scrolling del canvas."""
        self.app.central_canvas.configure(
            xscrollcommand=self.app.h_scrollbar.set,
            yscrollcommand=self.app.v_scrollbar.set,
        )
        self.app.central_canvas.bind("<Configure>", self.app._update_scrollbars)

    def _create_virtual_window(self, vw_height: int, vw_width: int) -> None:
        """Crea el VirtualWindow en el canvas."""
        from objects.window.virtual_window import VirtualWindow

        self.app.virtual_window = VirtualWindow(
            self.app.central_canvas,
            self.app.left_sidebar,
            self.app,
            width=vw_width,
            height=vw_height,
        )
        self.app.virtual_window_id = self.app.central_canvas.create_window(
            50, 50, anchor="nw", window=self.app.virtual_window
        )

    def _create_right_sidebar(self) -> None:
        """Crea la sidebar derecha."""
        from components.right_sidebar import RightSidebar

        self.app.right_sidebar = RightSidebar(
            self.app.main_frame, self.app.virtual_window, self.app
        )
        self.app.right_sidebar.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

    def _create_toolbar(self) -> None:
        """Crea la toolbar."""
        from components.toolbar import Toolbar

        self.app.toolbar = Toolbar(
            self.app,
            self.app.virtual_window,
            self.app.right_sidebar,
            self.app,
            self.current_project.import_project if self.current_project else False,
        )
        self.app.toolbar.grid(row=2, column=0, columnspan=4, sticky="ew")

    def _create_menu_system(self) -> None:
        """Crea el sistema de menús."""
        self.app._create_menu_system()

    def _handle_project_import(self) -> None:
        """Maneja la importación de proyectos si aplica."""
        if not (self.current_project and self.current_project.import_project):
            return

        file_path = filedialog.askopenfilename(
            filetypes=[(self.app.translator.translate("FILE_DIALOG_JSON_ARCHIVE"), "*.json")],
            title="Abrir archivo",
        )
        if file_path:
            self.app.virtual_window.import_from_json(file_path)
            logging.info(f"Proyecto importado desde: {file_path}")

    def _finalize_main_ui(self) -> None:
        """Finaliza la configuración de la UI principal."""
        self.app.central_canvas.configure(scrollregion=self.app.central_canvas.bbox("all"))

    def reset_window(self) -> None:
        """Reinicia la aplicación a la pantalla de setup."""
        # Limpiar todos los widgets
        for widget in self.app.winfo_children():
            widget.destroy()

        # Resetear configuración
        self.app.resizable(False, False)
        self.app.geometry("1000x600")
        self.current_project = None

        # Recrear UI inicial
        self.app._initialize_ui()
        logging.info("Ventana reiniciada a pantalla de setup")