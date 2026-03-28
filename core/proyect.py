"""
Proyect module - Modelo de datos de proyecto y UI de setup inicial
"""
import logging
import customtkinter as ctk
from typing import TYPE_CHECKING

from functions import validate_input
from data.commands import BUTTON_STYLE

if TYPE_CHECKING:
    from main import App


class Project:
    """Modelo simple que representa un proyecto."""

    def __init__(self, height: int = 500, width: int = 800, import_project: bool = False):
        self.height = height
        self.width = width
        self.import_project = import_project

    def __repr__(self) -> str:
        return f"Project(height={self.height}, width={self.width}, import={self.import_project})"


class ProjectSetupUI:
    """Interfaz de setup para crear/importar un proyecto.
    
    Maneja toda la UI de la pantalla inicial (campos de altura/anchura, botones).
    """

    def __init__(self, app: "App"):
        """Inicializa la UI de setup.
        
        Args:
            app: Instancia de la aplicación principal (App).
        """
        self.app = app
        self.setup_frame: ctk.CTkFrame | None = None
        self.hvar: ctk.StringVar | None = None
        self.wvar: ctk.StringVar | None = None

    def create_initial_interface(self) -> None:
        """Crea la interfaz completamente."""
        self._create_setup_frame()
        self._create_project_setup_ui()

    def _create_setup_frame(self) -> None:
        """Crea el frame contenedor para la pantalla de setup."""
        self.setup_frame = ctk.CTkFrame(
            self.app, corner_radius=15, fg_color="transparent"
        )
        self.setup_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        self.setup_frame.grid_columnconfigure((0, 1), weight=1)
        self.setup_frame.grid_rowconfigure(list(range(7)), weight=1)

    def _create_project_setup_ui(self) -> None:
        """Crea todos los elementos de la UI de setup."""
        self._create_title_section()
        self._create_configuration_section()
        self._create_input_fields()
        self._create_action_buttons()

    def _create_title_section(self) -> None:
        """Crea la sección de título."""
        ctk.CTkLabel(
            self.setup_frame,
            text=self.app.translator.translate("NEW_PROYECT"),
            font=self.app.TITLE_FONT,
            text_color=("gray10", "gray90"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=30, pady=(30, 10))

    def _create_configuration_section(self) -> None:
        """Crea la sección de configuración."""
        ctk.CTkLabel(
            self.setup_frame,
            text=self.app.translator.translate("WINDOW_CONFIG"),
            font=self.app.SUBTITLE_FONT,
            text_color=("gray20", "gray80"),
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=30, pady=(10, 20))

    def _create_input_fields(self) -> None:
        """Crea los campos de entrada de altura y anchura."""
        validate_command = self.app.register(validate_input)

        self.hvar = ctk.StringVar(value=str(self.app.DEFAULT_HEIGHT))
        self._create_labeled_entry("HEIGHT", self.hvar, 2, validate_command)

        self.wvar = ctk.StringVar(value=str(self.app.DEFAULT_WIDTH))
        self._create_labeled_entry("WIDTH", self.wvar, 3, validate_command)

    def _create_labeled_entry(
        self,
        label_key: str,
        text_var: ctk.StringVar,
        row: int,
        validate_command,
    ) -> None:
        """Helper para crear una entrada con etiqueta.
        
        Args:
            label_key: Clave del traductor para la etiqueta.
            text_var: Variable StringVar para la entrada.
            row: Número de fila en el grid.
            validate_command: Comando de validación registrado.
        """
        label_text = self.app.translator.translate(label_key)

        ctk.CTkLabel(
            self.setup_frame,
            text=label_text,
            font=self.app.LABEL_FONT,
            text_color=("gray10", "gray90"),
        ).grid(row=row, column=0, sticky="e", padx=(20, 10), pady=10)

        ctk.CTkEntry(
            self.setup_frame,
            textvariable=text_var,
            validate="key",
            validatecommand=(validate_command, "%P"),
            placeholder_text=text_var.get(),
            **self.app.ENTRY_STYLE,
        ).grid(row=row, column=1, sticky="w", padx=(10, 30), pady=10)

    def _create_action_buttons(self) -> None:
        """Crea los botones de Create e Import."""
        from core.proyect_manager import ProjectManager
        
        project_manager: ProjectManager = self.app.project_manager

        ctk.CTkButton(
            self.setup_frame,
            text=self.app.translator.translate("CREATE_PROJECT"),
            command=project_manager.create_project,
            font=self.app.LABEL_FONT,
            **BUTTON_STYLE,
        ).grid(row=8, column=0, sticky="se", padx=30, pady=30)

        ctk.CTkButton(
            self.setup_frame,
            text=self.app.translator.translate("IMPORT_PROJECT"),
            command=lambda: project_manager.create_project(import_project=True),
            font=self.app.LABEL_FONT,
            **BUTTON_STYLE,
        ).grid(row=8, column=1, sticky="sw", padx=30, pady=30)

    def cleanup(self) -> None:
        """Limpia la interfaz de setup."""
        if self.setup_frame and self.setup_frame.winfo_exists():
            for widget in self.setup_frame.winfo_children():
                widget.destroy()
            self.setup_frame.destroy()
            self.setup_frame = None