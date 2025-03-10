def validate_input(value:any):
    """Update the treeview in the right sidebar.

    This method triggers an update of the treeview widget within the right sidebar.
    It calls the `update_treeview` method of the `right_sidebar` object.

    Args:
        self: The current instance of the class.

    Returns:
        None
    """

    return bool(value == "" or (value.isdigit() and 0 <= int(value) <= 1000))

def hex_to_rgb(hex_color):
    """Convierte un color hexadecimal (#RRGGBB) a un tuple (R, G, B)."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def parse_color(color):
    """Convierte colores de CustomTkinter en formato RGB."""
    if isinstance(color, list):  # Si es una lista, toma el primer color
        color = color[0]
    if isinstance(color, str) and color.startswith("#"):  # Si es hexadecimal
        return hex_to_rgb(color)
    return (200, 200, 200)  # Color gris por defecto