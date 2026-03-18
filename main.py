# Version: 1.3 (refactored)

import contextlib
import io
import sys
import logging
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

# Internal modules — avoid wildcard imports
from config.config_manager import ConfigManager
from core.app import init_app
from data.commands import COMMAND_MAP, global_properties, BUTTON_STYLE, TOOLTIP_INFO_WIDGET
from functions import (
    validate_input,
    load_classes_from_file,
    clear_widgets,
    update_treeview,
    translator,
    enable_resizable_highlight,
)
from objects.code_box import CTkCodeBox
from objects.CTkMenuBar import CTkMenuBar, CustomDropdownMenu
from objects.window.virtual_window import VirtualWindow
from plugins.plugin_manager import PluginManager
from components.left_sidebar import LeftSidebar
from components.right_sidebar import RightSidebar
from components.toolbar import Toolbar


class App(ctk.CTk):
    """Main application class for CustomDesigner."""

    # Class constants
    DEFAULT_HEIGHT = 500
    DEFAULT_WIDTH = 800
    LEFT_SIDEBAR_MIN_WIDTH = 220
    RIGHT_SIDEBAR_MIN_WIDTH = 220
    CENTER_MIN_WIDTH = 360
    MAIN_MIN_HEIGHT = 560

    def __init__(self):
        # CustomTkinter appearance must be configured before super().__init__()
        self._apply_theme_from_config()
        super().__init__()

        # Initialize message queue state before any UI that might use it
        self.message_queue: list[str] = []
        self.is_showing_message = False

        self._initialize_core_components()
        self._setup_window()
        self._initialize_ui()
        self._initialize_plugins()

    # =========================================================================
    # THEME / APPEARANCE
    # =========================================================================

    def _apply_theme_from_config(self):
        """Resolve and apply theme before the window is created."""
        config_manager = ConfigManager()
        appearance_mode, color_theme = self._resolve_theme_config(config_manager)
        ctk.set_appearance_mode(appearance_mode)
        ctk.set_default_color_theme(color_theme)

    @staticmethod
    def _resolve_theme_config(config_manager: ConfigManager) -> tuple[str, str]:
        """Resolve stored theme value into appearance mode and color theme."""
        stored_theme = str(
            config_manager.get("General", "theme", fallback="dark-blue")
        ).strip().lower()

        if stored_theme in {"light", "dark", "system"}:
            return stored_theme, "dark-blue"

        if stored_theme in {"dark-blue", "blue", "green"}:
            return "dark", stored_theme

        logging.warning("Unknown theme '%s'. Falling back to dark/dark-blue.", stored_theme)
        return "dark", "dark-blue"

    # =========================================================================
    # INITIALIZATION
    # =========================================================================

    def _initialize_core_components(self):
        self.config_manager = ConfigManager()
        self.translator = translator
        self.command_history: list[str] = []

        self.import_project = False   # was: import_proyect (typo)
        self.use_scene_manager = False

    def _setup_window(self):
        """Configure application window properties."""
        self.title("CustomDesigner")
        self.geometry("1000x600")
        self.resizable(False, False)

    def _initialize_ui(self):
        """Initialize the complete UI structure."""
        self._setup_fonts_and_styles()
        self._setup_initial_layout()
        self._create_initial_interface()

    def _initialize_plugins(self):
        self.plugin_manager = PluginManager()
        self.plugin_manager.discover_plugins()
        self.plugin_manager.initialize_plugins(self)

    # =========================================================================
    # FONTS AND STYLES
    # =========================================================================

    def _setup_fonts_and_styles(self):
        """Define fonts and styling dictionaries."""
        self.TITLE_FONT = ctk.CTkFont(family="Helvetica", size=36, weight="bold")
        self.SUBTITLE_FONT = ctk.CTkFont(family="Helvetica", size=18)
        self.LABEL_FONT = ctk.CTkFont(family="Helvetica", size=14)

        self.ENTRY_STYLE = {
            "fg_color": "transparent",
            "border_width": 2,
            "border_color": "#1F6AA5",
            "text_color": ("gray10", "gray90"),
            "width": 140,
            "height": 35,
            "corner_radius": 8,
            "font": self.LABEL_FONT,
        }

        self.CHECKBOX_STYLE = {
            "fg_color": "#1F6AA5",
            "text_color": ("gray10", "gray90"),
            "hover_color": "#2980B9",
            "border_width": 2,
            "border_color": "#1F6AA5",
            "checkmark_color": ("gray90", "gray10"),
            "corner_radius": 5,
            "font": self.LABEL_FONT,
        }

    # =========================================================================
    # INITIAL PROJECT SETUP UI
    # =========================================================================

    def _setup_initial_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _create_initial_interface(self):
        self._create_setup_frame()
        self._create_project_setup_ui()

    def _create_setup_frame(self):
        """Create the container frame for the project-setup screen.

        Named 'setup_frame' to avoid colliding with self.virtual_window
        (which later holds the actual VirtualWindow widget).
        """
        self.setup_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.setup_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        self.setup_frame.grid_columnconfigure((0, 1), weight=1)
        self.setup_frame.grid_rowconfigure(list(range(7)), weight=1)

    def _create_project_setup_ui(self):
        self._create_title_section()
        self._create_configuration_section()
        self._create_input_fields()
        self._create_action_buttons()

    def _create_title_section(self):
        ctk.CTkLabel(
            self.setup_frame,
            text=self.translator.translate("NEW_PROYECT"),
            font=self.TITLE_FONT,
            text_color=("gray10", "gray90"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=30, pady=(30, 10))

    def _create_configuration_section(self):
        ctk.CTkLabel(
            self.setup_frame,
            text=self.translator.translate("WINDOW_CONFIG"),
            font=self.SUBTITLE_FONT,
            text_color=("gray20", "gray80"),
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=30, pady=(10, 20))

    def _create_input_fields(self):
        validate_command = self.register(validate_input)

        self.hvar = ctk.StringVar(value=str(self.DEFAULT_HEIGHT))
        self._create_labeled_entry("HEIGHT", self.hvar, 2, validate_command)

        self.wvar = ctk.StringVar(value=str(self.DEFAULT_WIDTH))
        self._create_labeled_entry("WIDTH", self.wvar, 3, validate_command)

    def _create_labeled_entry(self, label_key: str, text_var: ctk.StringVar, row: int, validate_command):
        label_text = self.translator.translate(label_key)

        ctk.CTkLabel(
            self.setup_frame,
            text=label_text,
            font=self.LABEL_FONT,
            text_color=("gray10", "gray90"),
        ).grid(row=row, column=0, sticky="e", padx=(20, 10), pady=10)

        ctk.CTkEntry(
            self.setup_frame,
            textvariable=text_var,
            validate="key",
            validatecommand=(validate_command, "%P"),
            placeholder_text=text_var.get(),
            **self.ENTRY_STYLE,
        ).grid(row=row, column=1, sticky="w", padx=(10, 30), pady=10)

    def _create_action_buttons(self):
        """Create the Create and Import buttons.

        Both buttons share row=8; they are differentiated by column so both
        are actually visible (column 0 and column 1, not 0 and 4).
        """
        ctk.CTkButton(
            self.setup_frame,
            text=self.translator.translate("CREATE_PROJECT"),
            command=self.create_project,
            font=self.LABEL_FONT,
            **BUTTON_STYLE,
        ).grid(row=8, column=0, sticky="se", padx=30, pady=30)

        ctk.CTkButton(
            self.setup_frame,
            text=self.translator.translate("IMPORT_PROJECT"),
            command=lambda: self.create_project(import_project=True),
            font=self.LABEL_FONT,
            **BUTTON_STYLE,
        ).grid(row=8, column=1, sticky="sw", padx=30, pady=30)

    # =========================================================================
    # PROJECT CREATION AND TRANSITION
    # =========================================================================

    def create_project(self, import_project: bool = False):
        """Handle project creation with specified dimensions."""
        self.import_project = import_project
        self._transition_to_main_ui(self.hvar.get(), self.wvar.get())

    def _transition_to_main_ui(self, height: str, width: str):
        height = str(height) if isinstance(height, int) else height
        width = str(width) if isinstance(width, int) else width

        if not (height.isdigit() and width.isdigit()):
            logging.warning("Altura o anchura no válidas: height=%s, width=%s", height, width)
            return

        self._cleanup_setup_interface()
        self._create_main_ui(int(height), int(width))
        self._setup_debug_features()

    def _cleanup_setup_interface(self):
        for widget in self.setup_frame.winfo_children():
            widget.destroy()
        self.setup_frame.destroy()

    def reset_window(self):
        """Reset the window to its default project-setup state."""
        for widget in self.winfo_children():
            widget.destroy()
        self.resizable(False, False)
        self.geometry("1000x600")
        self._initialize_ui()

    # =========================================================================
    # MAIN UI
    # =========================================================================

    def _create_main_ui(self, vw_height: int, vw_width: int):
        self._setup_main_layout()
        self._create_main_components(vw_height, vw_width)
        self._create_menu_system()
        self._handle_project_import()
        self._finalize_main_ui()

    def _setup_main_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        min_window_width = (
            self.LEFT_SIDEBAR_MIN_WIDTH
            + self.RIGHT_SIDEBAR_MIN_WIDTH
            + self.CENTER_MIN_WIDTH
            + 40
        )
        self.minsize(min_window_width, self.MAIN_MIN_HEIGHT)
        self.resizable(True, True)

    def _create_main_components(self, vw_height: int, vw_width: int):
        self._create_main_frame()
        self._create_left_sidebar()
        self._create_central_workspace(vw_height, vw_width)
        self._create_right_sidebar()
        self._create_toolbar()

    def _create_main_frame(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, columnspan=4, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=0, minsize=self.LEFT_SIDEBAR_MIN_WIDTH)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=0, minsize=self.RIGHT_SIDEBAR_MIN_WIDTH)
        self.main_frame.grid_rowconfigure(0, weight=1)

    def _create_left_sidebar(self):
        """Create the left sidebar."""
        self.left_sidebar = LeftSidebar(self.main_frame, self)  # was: app (global)
        self.left_sidebar.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    def _create_central_workspace(self, vw_height: int, vw_width: int):
        self._create_central_frame()
        self._create_canvas_with_scrollbars()
        self._create_virtual_window(vw_height, vw_width)

    def _create_central_frame(self):
        self.central_frame = ctk.CTkFrame(self.main_frame)
        self.central_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.central_frame.grid_columnconfigure(0, weight=1)
        self.central_frame.grid_rowconfigure(0, weight=1)

    def _create_canvas_with_scrollbars(self):
        self.central_canvas = tk.Canvas(self.central_frame, bg="black")
        self.central_canvas.grid(row=0, column=0, sticky="nsew")
        self._create_scrollbars()
        self._configure_canvas_scrolling()

    def _create_scrollbars(self):
        self.h_scrollbar = ctk.CTkScrollbar(
            self.central_frame,
            orientation="horizontal",
            command=self.central_canvas.xview,
        )
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.v_scrollbar = ctk.CTkScrollbar(
            self.central_frame,
            orientation="vertical",
            command=self.central_canvas.yview,
        )
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")

    def _configure_canvas_scrolling(self):
        self.central_canvas.configure(
            xscrollcommand=self.h_scrollbar.set,
            yscrollcommand=self.v_scrollbar.set,
        )
        self.central_canvas.bind("<Configure>", self._update_scrollbars)

    def _create_virtual_window(self, vw_height: int, vw_width: int):
        """Create the VirtualWindow widget on the canvas."""
        self.virtual_window = VirtualWindow(
            self.central_canvas,
            self.left_sidebar,
            self,
            width=vw_width,
            height=vw_height,
        )
        self.virtual_window_id = self.central_canvas.create_window(
            50, 50, anchor="nw", window=self.virtual_window
        )

    def _create_right_sidebar(self):
        """Create the right sidebar (requires virtual_window to exist first)."""
        self.right_sidebar = RightSidebar(self.main_frame, self.virtual_window, self)  # was: app
        self.right_sidebar.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

    def _create_toolbar(self):
        """Create the bottom toolbar (requires virtual_window and right_sidebar)."""
        self.toolbar = Toolbar(
            self, self.virtual_window, self.right_sidebar, self, self.import_project  # was: app
        )
        self.toolbar.grid(row=2, column=0, columnspan=4, sticky="ew")

    def _handle_project_import(self):
        if not self.import_project:
            return
        file_path = filedialog.askopenfilename(
            filetypes=[(self.translator.translate("FILE_DIALOG_JSON_ARCHIVE"), "*.json")],
            title="Abrir archivo",
        )
        if file_path:
            self.virtual_window.import_from_json(file_path)

    def _finalize_main_ui(self):
        self.central_canvas.configure(scrollregion=self.central_canvas.bbox("all"))

    # =========================================================================
    # MENU SYSTEM
    # =========================================================================

    def _create_menu_system(self):
        self._create_menu_container()
        self._create_menu_bar()
        self._setup_menu_dropdowns()

    def _create_menu_container(self):
        self.menu_container = ctk.CTkFrame(self, height=25)
        self.menu_container.grid(row=0, column=0, columnspan=4, sticky="ew")
        self.menu_container.grid_propagate(False)

    def _create_menu_bar(self):
        self.menu_bar = CTkMenuBar(
            self.menu_container,
            height=20,
            bg_color="#1a1a1a",
            padx=0,
            pady=0,
        )
        self.menu_button = self.menu_bar.add_cascade(
            text=self.translator.translate("MENU_BAR_MENU_TITLE")
        )
        self.tool_button = self.menu_bar.add_cascade(
            text=self.translator.translate("MENU_BAR_TOOL_TITLE")
        )

    _DROPDOWN_STYLE = dict(
        width=150,
        fg_color="#2b2b2b",
        hover_color="#1f1f1f",
        corner_radius=8,
        border_width=1,
        border_color="grey30",
    )

    def _make_dropdown(self, widget) -> "CustomDropdownMenu":
        return CustomDropdownMenu(widget=widget, master=self, **self._DROPDOWN_STYLE)

    def _setup_menu_dropdowns(self):
        self.menu_button_drop = self._make_dropdown(self.menu_button)
        self.tool_button_drop = self._make_dropdown(self.tool_button)
        plugin_cascade = self.menu_bar.add_cascade(text="Plugins")
        self.plugin_button_drop = self._make_dropdown(plugin_cascade)

        self._populate_menu_options()
        self._populate_tools_options()
        self._populate_plugins_options()

    def _add_options_to_dropdown(self, dropdown, options: list):
        """Generic helper: adds (text, command) tuples or 'separator' strings."""
        for option in options:
            if option == "separator":
                dropdown.add_separator()
            else:
                text, command = option
                dropdown.add_option(text, command=command)

    def _populate_menu_options(self):
        self._add_options_to_dropdown(self.menu_button_drop, [
            (self.translator.get("project.NEW_PROYECT"), self.reset_window),
            "separator",
            (self.translator.translate("TOOL_BUTTON_EXPORT"), self.toolbar.export_to_file),
            (self.translator.translate("TOOL_BUTTON_CONFIG"), self.toolbar.open_config_window),
            "separator",
            (self.translator.get("menubar.exit_option"), self.quit),
        ])

    def _populate_tools_options(self):
        self._add_options_to_dropdown(self.tool_button_drop, [
            (self.translator.translate("CONSOLE_BUTTON_TEXT"), self.toolbar.open_console),
            "separator",
        ])

    def _populate_plugins_options(self):
        self._add_options_to_dropdown(self.plugin_button_drop, [
            (self.translator.get("plugin_window.plugins_manager"), self.open_plugin_manager),
            "separator",
        ])

    # =========================================================================
    # PLUGIN MANAGER
    # =========================================================================

    def open_plugin_manager(self):
        """Open plugin manager window (creates it on first call, raises on subsequent)."""
        if not hasattr(self, "plugin_window") or not self.plugin_window.winfo_exists():
            self.plugin_window = ctk.CTkToplevel(self)
            self.plugin_window.title(self.translator.get("plugin_window.window_title"))
            self.plugin_window.geometry("400x600")
            self._create_plugin_manager_ui()
        else:
            self.plugin_window.lift()

    def _create_plugin_manager_ui(self):
        frame = ctk.CTkScrollableFrame(self.plugin_window)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(
            frame,
            text=self.translator.get("plugin_window.header_text"),
            font=("Helvetica", 16, "bold"),
        ).pack(pady=10)

        if not self.plugin_manager.plugins:
            ctk.CTkLabel(frame, text=self.translator.get("plugin_window.no_plugins")).pack(pady=20)
            return

        for name, plugin in self.plugin_manager.plugins.items():
            self._create_plugin_entry(frame, name, plugin)

    def _create_plugin_entry(self, parent, name: str, plugin):
        plugin_frame = ctk.CTkFrame(parent)
        plugin_frame.pack(fill="x", padx=5, pady=5)

        info_frame = ctk.CTkFrame(plugin_frame)
        info_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(info_frame, text=name, font=("Helvetica", 14, "bold")).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=f"Version: {plugin.version}").pack(anchor="w")
        ctk.CTkLabel(
            info_frame,
            text=f"{self.translator.get('plugin_window.plugin_author')} {plugin.author}",
        ).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=plugin.description, wraplength=300).pack(anchor="w")

        switch = ctk.CTkSwitch(plugin_frame, text="Enabled")
        switch.configure(command=lambda p=name, s=switch: self._toggle_plugin(p, s))
        switch.pack(pady=5)

        if self.plugin_manager.enabled_plugins.get(name, True):
            switch.select()
        else:
            switch.deselect()

        if name == "Base Plugin":
            switch.configure(state="disabled")

    def _toggle_plugin(self, plugin_name: str, switch: ctk.CTkSwitch):
        if switch.get():
            self.plugin_manager.enable_plugin(plugin_name)
        else:
            self.plugin_manager.disable_plugin(plugin_name)

    # =========================================================================
    # SCROLLBAR MANAGEMENT
    # =========================================================================

    def _update_scrollbars(self, event=None):
        bbox = self.central_canvas.bbox("all")
        if not bbox:
            return

        canvas_width = self.central_canvas.winfo_width()
        canvas_height = self.central_canvas.winfo_height()

        if bbox[2] - bbox[0] > canvas_width:
            self.h_scrollbar.grid()
        else:
            self.h_scrollbar.grid_remove()

        if bbox[3] - bbox[1] > canvas_height:
            self.v_scrollbar.grid()
        else:
            self.v_scrollbar.grid_remove()

    # =========================================================================
    # LANGUAGE / UI REFRESH
    # =========================================================================

    def switch_language(self, language: str):
        try:
            self.translator.set_language(language)
            self.refresh_ui()
        except ValueError as e:
            self.cross_update_text_info(str(e))

    def refresh_ui(self):
        for component in (self.toolbar, self.left_sidebar, self.right_sidebar):
            self._refresh_component_text(component)

    def _refresh_component_text(self, component):
        for widget in component.winfo_children():
            if isinstance(widget, (ctk.CTkLabel, ctk.CTkButton)):
                with contextlib.suppress(Exception):
                    key = self.translator.find_key_by_value(widget.cget("text"))
                    widget.configure(text=self.translator.translate(key))

    # =========================================================================
    # WIDGET MANAGEMENT
    # =========================================================================

    def inter_add_widget(self, widget):
        kwargs_dict = self._extract_widget_properties(widget)
        self.virtual_window.paste_widget(widget, **kwargs_dict)

    def _extract_widget_properties(self, widget) -> dict:
        widget_class = widget.__class__.__name__
        kwargs_dict = {}
        for prop in global_properties.get(widget_class, []):
            with contextlib.suppress(Exception):
                kwargs_dict[prop] = widget.cget(prop)
        return kwargs_dict

    # =========================================================================
    # CROSS-COMPONENT COMMUNICATION
    # =========================================================================

    def cross_update_treeview(self):
        self.right_sidebar.update_treeview()

    def cross_update_progressbar(self, val):
        self.toolbar.progress_set_value(val)

    def cross_update_text_info(self, val: str):
        """Queue a status message for the toolbar info label."""
        self.message_queue.append(val)
        if not self.is_showing_message:
            self._process_message_queue()

    # =========================================================================
    # MESSAGE QUEUE
    # =========================================================================

    def _process_message_queue(self):
        if not self.message_queue or not hasattr(self, "toolbar"):
            self.is_showing_message = False
            return

        message = self.message_queue.pop(0)
        self.is_showing_message = True
        pending = len(self.message_queue)
        display = f"{message} ({pending} more)" if pending else message
        self.toolbar.info_label.configure(text=display)
        self.after(3000, self._show_next_message)

    def _show_next_message(self):
        if self.message_queue:
            self._process_message_queue()
        else:
            with contextlib.suppress(AttributeError):
                self.toolbar.info_label.configure(text="Ok.")
            self.is_showing_message = False

    # =========================================================================
    # CONSOLE
    # =========================================================================

    def open_console(self):
        console = self._create_console_window()
        state = self._initialize_console_state()
        output_textbox = self._create_console_output(console)
        _, input_entry = self._create_console_input(console)
        self._setup_console_commands(state, output_textbox, input_entry)
        self._bind_console_events(input_entry, state)

    def _create_console_window(self) -> ctk.CTkToplevel:
        console = ctk.CTkToplevel(self)
        console.title(self.translator.translate("CONSOLE_BUTTON_TEXT"))
        console.geometry("600x400")
        console.after(100, console.lift)
        return console

    @staticmethod
    def _initialize_console_state() -> dict:
        return {"command_history": [], "history_index": -1, "custom_command_active": False}

    @staticmethod
    def _create_console_output(console) -> ctk.CTkTextbox:
        output = ctk.CTkTextbox(console, width=580, height=300, wrap="word")
        output.pack(pady=10, padx=10)
        output.configure(state="disabled")
        return output

    def _create_console_input(self, console) -> tuple:
        input_frame = ctk.CTkFrame(console)
        input_frame.pack(fill="x", padx=10, pady=5)

        input_entry = ctk.CTkEntry(input_frame, width=480)
        input_entry.pack(side="left", padx=(0, 5), fill="x", expand=True)

        ctk.CTkButton(
            input_frame,
            text=self.translator.translate("CONSOLE_BUTTON_RUN"),
        ).pack(side="right")

        return input_frame, input_entry

    def _setup_console_commands(self, state, output_textbox, input_entry):
        def execute():
            self._execute_console_command(state, output_textbox, input_entry)

        input_entry.bind("<Return>", lambda _: execute())
        execute_button = input_entry.master.winfo_children()[-1]
        execute_button.configure(command=execute)

    def _execute_console_command(self, state, output_textbox, input_entry):
        command = input_entry.get()
        if not command.strip():
            return

        output_textbox.configure(state="normal")
        try:
            self._run_command(command, output_textbox, state)
            state["command_history"].append(command)
        except Exception as e:
            output_textbox.insert(ctk.END, f"> {command}\nError: {e}\n")
        finally:
            input_entry.delete(0, ctk.END)
            output_textbox.configure(state="disabled")

    def _run_command(self, command: str, output_textbox, state):
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = io.StringIO()

        try:
            if command.startswith("$"):
                state["custom_command_active"] = True
                self._handle_custom_command(command[1:])
            else:
                state["custom_command_active"] = False
                result = eval(command)  # noqa: S307
                if result is not None:
                    print(result)

            output = sys.stdout.getvalue()
            error = sys.stderr.getvalue()
            output_textbox.insert(ctk.END, f"> {command}\n{output}{error}\n")
            output_textbox.see(ctk.END)
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr

    def _handle_custom_command(self, cmd: str):
        parts = cmd.split(maxsplit=1)
        command = parts[0]
        args = parts[1].split() if len(parts) > 1 else []

        if command not in COMMAND_MAP:
            print(f"Unknown command: {cmd}")
            return
        try:
            self._execute_mapped_command(command, args)
        except TypeError:
            print(f"Usage error: run 'help' for correct usage of '{command}'")

    def _execute_mapped_command(self, command: str, args: list):
        no_arg = {"clear", "exit"}
        app_only = {
            "list_widgets", "show_config", "undo", "redo",
            "debug_widgets", "clean_widgets", "debug_undo_stack",
            "debug_redo_stack", "export_img", "inspect_events",
        }
        app_with_args = {
            "change_theme", "change_language", "save_project",
            "load_project", "show_widget_info", "run_code",
            "export_json", "import_json", "exec",
        }

        if command in no_arg:
            COMMAND_MAP[command](self if command == "exit" else None)
        elif command in app_only:
            COMMAND_MAP[command](self)
        elif command in app_with_args:
            COMMAND_MAP[command](self, args)
        else:
            COMMAND_MAP[command]([])

    def _bind_console_events(self, input_entry, state):
        input_entry.bind("<Up>", lambda _: self._browse_command_history(input_entry, state, -1))
        input_entry.bind("<Down>", lambda _: self._browse_command_history(input_entry, state, 1))
        input_entry.bind(
            "<KeyRelease>",
            lambda _: state.update(custom_command_active=input_entry.get().startswith("$")),
        )

    def _browse_command_history(self, input_entry, state, direction: int):
        history = state["command_history"]
        if not history:
            return

        state["history_index"] = max(
            0, min(state["history_index"] + direction, len(history))
        )
        input_entry.delete(0, ctk.END)
        if state["history_index"] < len(history):
            input_entry.insert(0, history[state["history_index"]])

    # =========================================================================
    # DEBUG FEATURES
    # =========================================================================

    def _setup_debug_features(self):
        if TOOLTIP_INFO_WIDGET:
            self.toolbar.create_button("Debug Grid", self.display_grid_debug, "right")
        self.display_tooltip()

    def mark_widget_with_color(self, widget, color: str = "red"):
        if not hasattr(widget, "configure"):
            logging.warning("Widget doesn't have 'configure' method.")
            return

        previous_color = widget.cget("fg_color")
        widget.configure(fg_color=color)

        if hasattr(self, "widget_marked_color") and self.widget_marked_color:
            self.widget_marked_color.configure(fg_color=previous_color)
        self.widget_marked_color = widget

    def display_tooltip(self):
        if not TOOLTIP_INFO_WIDGET:
            return

        for widget in (
            self.main_frame, self.toolbar, self.left_sidebar,
            self.right_sidebar, self.virtual_window, self.menu_bar,
        ):
            tooltip = CTkToolTip(
                widget,
                message=self._generate_tooltip_text(widget),
                alpha=0.9,
                font=("Consolas", 11),
                delay=0.5,
            )
            tooltip.show()

    def _generate_tooltip_text(self, widget) -> str:
        lines = [
            f"Widget: {widget.__class__.__name__}",
            f"Position: ({widget.winfo_x()}, {widget.winfo_y()})",
            f"Size: {widget.winfo_width()}x{widget.winfo_height()}",
        ]
        try:
            lines.append(f"Grid Info: {widget.grid_info()}")
        except Exception:
            lines.append("Grid Info: N/A")

        widget_class = widget.__class__.__name__
        if widget_class in global_properties:
            lines.append("\nProperties:")
            for prop in global_properties[widget_class]:
                with contextlib.suppress(Exception):
                    lines.append(f"  {prop}: {widget.cget(prop)}")

        lines.append(f"\nChildren Count: {len(widget.winfo_children())}")
        return "\n".join(lines)

    def display_grid_debug(self):
        debug_canvas = self._create_debug_canvas()
        cell_w, cell_h = self._draw_grid_lines(debug_canvas)
        self._draw_widget_cells(debug_canvas, cell_w, cell_h)
        self._add_debug_close_button(debug_canvas)

    def _create_debug_canvas(self) -> tk.Canvas:
        canvas = tk.Canvas(self.main_frame, highlightthickness=0, bg="#000001")
        canvas.place(
            x=0, y=0,
            width=self.main_frame.winfo_width(),
            height=self.main_frame.winfo_height(),
        )
        return canvas

    def _draw_grid_lines(self, canvas: tk.Canvas) -> tuple[float, float]:
        """Draw grid lines and return (cell_width, cell_height)."""
        GRID_COLOR = "#FF0000"
        cols, rows = self.main_frame.grid_size()
        w = self.main_frame.winfo_width()
        h = self.main_frame.winfo_height()
        cell_w, cell_h = w / cols, h / rows

        for i in range(rows + 1):
            y = i * cell_h
            canvas.create_line(0, y, w, y, fill=GRID_COLOR, dash=(4, 2))

        for i in range(cols + 1):
            x = i * cell_w
            canvas.create_line(x, 0, x, h, fill=GRID_COLOR, dash=(4, 2))

        return cell_w, cell_h

    def _draw_widget_cells(self, canvas: tk.Canvas, cell_w: float, cell_h: float):
        """Draw widget cell overlays — reuses dimensions from _draw_grid_lines."""
        CELL_COLOR = "#00FF00"
        TEXT_COLOR = "#FFFFFF"

        for widget in self.main_frame.winfo_children():
            if not widget.winfo_viewable():
                continue
            grid_info = widget.grid_info()
            if grid_info:
                self._draw_widget_cell(canvas, widget, grid_info, cell_w, cell_h, CELL_COLOR, TEXT_COLOR)

    def _draw_widget_cell(self, canvas, widget, grid_info, cell_w, cell_h, cell_color, text_color):
        row = grid_info["row"]
        col = grid_info["column"]
        rowspan = grid_info.get("rowspan", 1)
        colspan = grid_info.get("colspan", 1)

        x1, y1 = col * cell_w, row * cell_h
        x2, y2 = x1 + cell_w * colspan, y1 + cell_h * rowspan

        canvas.create_rectangle(x1, y1, x2, y2, outline=cell_color, width=2)
        canvas.create_text(
            (x1 + x2) / 2, (y1 + y2) / 2,
            text=f"{widget.__class__.__name__}\n({row},{col})\nspan:({rowspan},{colspan})",
            fill=text_color,
            font=("Consolas", 8),
        )

    def _add_debug_close_button(self, canvas: tk.Canvas):
        ctk.CTkButton(canvas, text="Close Grid Debug", command=canvas.destroy).place(x=10, y=10)

if __name__ == "__main__":
    app = App()
    init_app(app)
    app.mainloop()