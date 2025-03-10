import customtkinter as ctk

def cmd_hello(_):
    print("Hello, Custom Console!")

def cmd_clear(output_textbox):
    output_textbox.delete("1.0", ctk.END)

def cmd_help(_):
    help_text = """Available commands:
    - hello: Displays a hello message
    - clear: Clears the console output
    - help: Displays this help message
    - exit: Closes the console
    - list_widgets: Lists all widgets in the virtual window
    - change_theme <theme>: Changes the application theme
    - change_language <language>: Changes the application language
    - show_config: Displays the current configuration
    - save_project <filename>: Saves the current project to a file //Unused
    - load_project <filename>: Loads a project from a file //Unused
    - undo: Undoes the last action
    - redo: Redoes the last undone action
    - toggle_appearance_mode: Toggles between light and dark modes
    - show_widget_info <widget_name>: Shows detailed information about a widget
    - run_code <code>: Executes a snippet of Python code
    - export_json <filename>: Exports project as JSON
    - import_json <filename>: Imports project from JSON
    - debug_widgets: Shows widget properties
    - clean_widgets: Deletes all widgets
    """
    print(help_text)

def cmd_export_img(app):
    app.virtual_window.export_to_image("screenshot.png")

def cmd_exit(console):
    console.destroy()

def cmd_list_widgets(app):
    for widget in app.virtual_window.widgets:
        print(f"Widget: {widget.__class__.__name__}, ID: {id(widget)}")

def cmd_change_theme(app, args):
    theme = args[0]
    ctk.set_default_color_theme(theme)
    print(f"Theme changed to {theme}")

def cmd_change_language(app, args):
    language = args[0]
    app.switch_language(language)
    print(f"Language changed to {language}")

def cmd_show_config(app):
    config = app.config_manager.config
    for section in config.sections():
        print(f"[{section}]")
        for key, value in config.items(section):
            print(f"{key} = {value}")

def cmd_save_project(app, args):
    filename = args[0]
    app.virtual_window.export_to_file(filename)
    print(f"Project saved to {filename}")

def cmd_load_project(app, args):
    filename = args[0]
    app.virtual_window.import_from_file(filename)
    print(f"Project loaded from {filename}")

def cmd_undo(app):
    app.virtual_window.undo()
    print("Last action undone")

def cmd_redo(app):
    app.virtual_window.redo()
    print("Last undone action redone")

def cmd_toggle_appearance_mode(_):
    current_mode = ctk.get_appearance_mode()
    print(current_mode)
    new_mode = "Dark" if current_mode == "Light" else "Light"
    ctk.set_appearance_mode(new_mode)
    print(f"Appearance mode toggled to {new_mode}")

def cmd_show_widget_info(app, args):
    widget_name = args[0]
    widget = app.virtual_window.find_widget_by_name(widget_name)
    print(f"Widget Info: {widget}" if widget else f"No widget found with name {widget_name}")

def cmd_run_code(_, args):
    code = " ".join(args)
    exec(code)
    print("Code executed")

def cmd_find_replace(app, args):
    find_text, replace_text = args
    app.virtual_window.find_replace(find_text, replace_text)
    print(f"Replaced '{find_text}' with '{replace_text}'")

def cmd_export_json(app, args):
    filename = args[0]
    app.virtual_window.export_to_json(filename)
    print(f"Proyecto exportado a {filename}.json")

def cmd_import_json(app, args):
    filename = args[0]
    app.virtual_window.import_from_json(filename)
    print(f"Proyecto importado desde {filename}.json")

def cmd_debug_widgets(app):
    for widget in app.virtual_window.widgets:
        print(f"Widget: {widget.__class__.__name__}, ID: {id(widget)}, Propiedades: {widget.configure()}")
        
def cmd_clear_all_widgets(app):
    app.virtual_window.clean_virtual_window()
    print("All widgets deleted")
    
def cmd_debug_undo_stack(app):
    print(app.virtual_window.undo_stack)
    
def cmd_debug_redo_stack(app):
    print(app.virtual_window.redo_stack)

# Diccionario de comandos
COMMAND_MAP = {
    "hello": cmd_hello,
    "clear": cmd_clear,
    "help": cmd_help,
    "exit": cmd_exit,
    "list_widgets": cmd_list_widgets,
    "change_theme": cmd_change_theme,
    "change_language": cmd_change_language,
    "show_config": cmd_show_config,
    "save_project": cmd_save_project,
    "load_project": cmd_load_project,
    "undo": cmd_undo,
    "redo": cmd_redo,
    "toggle_appearance_mode": cmd_toggle_appearance_mode,
    "show_widget_info": cmd_show_widget_info,
    "run_code": cmd_run_code,
    "export_json": cmd_export_json,
    "import_json": cmd_import_json,
    "debug_widgets": cmd_debug_widgets,
    "clean_widgets": cmd_clear_all_widgets,
    "debug_undo_stack": cmd_debug_undo_stack,
    "debug_redo_stack": cmd_debug_redo_stack,
    "export_img": cmd_export_img,
}
