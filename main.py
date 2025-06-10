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
from objects.window.virtual_window import VirtualWindow
#BETA
from plugins.plugin_manager import PluginManager
from objects.CTkMenuBar import *
from components.left_sidebar import *
from components.right_sidebar import *
from components.toolbar import Toolbar
from core.app import *

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
        self._initialize_plugins()
        
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
    
    def _initialize_plugins(self):
        self.plugin_manager = PluginManager()
        # Load plugins
        self.plugin_manager.discover_plugins()
        self.plugin_manager.initialize_plugins(self)
        
    def open_plugin_manager(self):
        """Open plugin manager window"""
        if not hasattr(self, 'plugin_window'):
            self.plugin_window = ctk.CTkToplevel(self)
            self.plugin_window.title(translator.get("plugin_window.window_title"))
            self.plugin_window.geometry("400x600")
            self._create_plugin_manager_ui()
        else:
            self.plugin_window.lift()
            
    def _create_plugin_manager_ui(self):
        """Create plugin manager UI"""
        frame = ctk.CTkScrollableFrame(self.plugin_window)
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Header
        header = ctk.CTkLabel(frame, text=translator.get("plugin_window.header_text"), font=("Helvetica", 16, "bold"))
        header.pack(pady=10)
        
        # Plugin list
        if len(self.plugin_manager.plugins.items())!=0:
            for name, plugin in self.plugin_manager.plugins.items():
                plugin_frame = ctk.CTkFrame(frame)
                plugin_frame.pack(fill="x", padx=5, pady=5)
                
                # Plugin info
                info_frame = ctk.CTkFrame(plugin_frame)
                info_frame.pack(fill="x", padx=5, pady=5)
                
                ctk.CTkLabel(info_frame, text=name, font=("Helvetica", 14, "bold")).pack(anchor="w")
                ctk.CTkLabel(info_frame, text=f"Version: {plugin.version}").pack(anchor="w")
                ctk.CTkLabel(info_frame, text=f"{translator.get('plugin_window.plugin_author')} {plugin.author}").pack(anchor="w")
                ctk.CTkLabel(info_frame, text=plugin.description, wraplength=300).pack(anchor="w")
                
                # Create switch first
                switch = ctk.CTkSwitch(plugin_frame, text="Enabled")
                
                # Now we can safely reference switch in the lambda
                switch.configure(command=lambda p=name, s=switch: self._toggle_plugin(p, s))
                
                switch.pack(pady=5)
                # Set initial state
                switch.select() if self.plugin_manager.enabled_plugins.get(name, True) else switch.deselect()
                
                if name == 'Base Plugin':
                    switch.configure(state="disabled")
        else:
            ctk.CTkLabel(frame, text=translator.get("plugin_window.no_plugins")).pack(pady=20)
            
    def _toggle_plugin(self, plugin_name: str, switch: ctk.CTkSwitch):
        """Toggle plugin enabled state"""
        if switch.get():
            self.plugin_manager.enable_plugin(plugin_name)
        else:
            self.plugin_manager.disable_plugin(plugin_name)
        
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
        self.plugin_button_drop = CustomDropdownMenu(
            widget=self.menu_bar.add_cascade(text="Plugins"),
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
        self._populate_plugins_options()
        
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
                
    def _populate_plugins_options(self):
        """Create the plugins dropdown menu with options."""
        plugins_options = [
            (translator.get("plugin_window.plugins_manager"), self.open_plugin_manager),
            "separator",
        ]        
        for option in plugins_options:
            if option == "separator":
                self.plugin_button_drop.add_separator()
            else:
                text, command = option
                self.plugin_button_drop.add_option(text, command=command)   
                 
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
        self.left_sidebar = LeftSidebar(self.main_frame, app)
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
        self.right_sidebar = RightSidebar(self.main_frame, self.virtual_window, app)
        self.right_sidebar.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

    def _create_toolbar(self):
        """Create the bottom toolbar."""
        self.toolbar = Toolbar(self, self.virtual_window, self.right_sidebar, app, self.import_proyect)
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
    init_app(app)
    app.mainloop()