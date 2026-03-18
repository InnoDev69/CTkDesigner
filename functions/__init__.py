"""
Functions module - Utilidades reutilizables para CTkDesigner.

Expone las funciones públicas de cada submódulo.
"""

# Generic utilities
from .generic import validate_input, hex_to_rgb, parse_color, fix_color_format

# Widget utilities
from .import_widget import load_classes_from_file, get_class_parameters
from .widget_resize import enable_resizable_highlight, remove_remark

# UI utilities
from .sidebars_utils import (
    clear_widgets,
    update_treeview,
    create_property_entry,
    create_property_entries,
)

# Animation utilities
from .create_widget_animation import create_widget_with_animation

# Translator manager
from .translator_manager import translator, initialize_translator

__all__ = [
    # Generic
    "validate_input",
    "hex_to_rgb",
    "parse_color",
    "fix_color_format",
    # Import/Widget
    "load_classes_from_file",
    "get_class_parameters",
    "enable_resizable_highlight",
    "remove_remark",
    # Sidebars
    "clear_widgets",
    "update_treeview",
    "create_property_entry",
    "create_property_entries",
    # Animation
    "create_widget_with_animation",
    # Translator
    "translator",
    "initialize_translator",
]