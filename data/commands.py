import customtkinter as ctk
from data.variable import *
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

# Función para registrar eventos
def register_event(widget, sequence, callback):
    """
    Registra un evento vinculado a un widget.
    
    Args:
        widget: El widget al que se vincula el evento
        sequence: La secuencia del evento (ej. "<Button-1>")
        callback: La función de callback
    """
    if widget not in event_registry:
        event_registry[widget] = {}
    
    event_registry[widget][sequence] = callback
    
    # Realiza la vinculación real
    widget.bind(sequence, callback)

# Función para mostrar eventos registrados
def display_registered_events(_):
    """
    Muestra todos los eventos registrados en la consola.
    """
    for widget, events in event_registry.items():
        if events:
            print(f"Widget: {widget}")
            for event, callback in events.items():
                print(f"  Evento: {event}, Callback: {callback}")
def execute_method(app, args):
    """
    Ejecuta dinámicamente un método de una clase.
    Uso: $exec <class_name> <method_name> [args...]
    Example: $exec VirtualWindow add_widget CTkButton
    """
    if len(args) < 2:
        print("Usage: $exec <class_name> <method_name> [args...]")
        return

    class_name = args[0]
    method_name = args[1]
    method_args = args[2:] if len(args) > 2 else []

    try:
        # Obtiene la instancia de la clase
        instance = None
        if hasattr(app, class_name.lower()):
            instance = getattr(app, class_name.lower())
        else:
            # Busca la instancia en comun con el atributo similar
            for attr in dir(app):
                obj = getattr(app, attr)
                if obj.__class__.__name__ == class_name:
                    instance = obj
                    break

        if instance is None:
            print(f"Class {class_name} not found")
            return

        # Nose, obtiene algo de la clase
        if hasattr(instance, method_name):
            method = getattr(instance, method_name)
            result = method(*method_args)
            print("Method executed successfully")
            if result is not None:
                print(f"Result: {result}")
        else:
            print(f"Method {method_name} not found in class {class_name}")

    except Exception as e:
        print(f"Error executing method: {str(e)}")
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
    "inspect_events": display_registered_events,
    "exec": execute_method,
}
