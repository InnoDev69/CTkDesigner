import customtkinter as ctk

# DEBUG
TOOLTIP_INFO_WIDGET = False

global_properties = {
    "VirtualWindow": ["width", "height", "fg_color", "bg_color", "border_width", "border_color"],
    "CTkButton": ["text", "command", "fg_color", "width", "height", "border_width", "border_color", "hover_color", "text_color",
                  "border_spacing", "corner_radius", "text_color_disabled", "textvariable", "image",
                  "state", "compound","anchor"],
    "CTkLabel": ["text", "textvariable", "fg_color", "corner_radius", "text_color", "width", "height", "font", "anchor", "compound",
                 "justify", "image"],
    "CTkEntry": ["placeholder_text", "textvariable", "fg_color", "border_width", "border_color", "text_color", "width", "height", "font"],
    "CTkCheckBox": ["text", "textvariable", "onvalue", "offvalue", "fg_color", "text_color", "width", "height", "hover_color",
                    "border_width", "border_color", "checkmark_color"],
    "CTkRadioButton": ["text", "command", "textvariable", "value", "fg_color", "text_color", "width", "height", "hover_color",
                       "border_color"],
    "CTkComboBox": ["values", "command", "state", "fg_color", "button_color", "button_hover_color", "dropdown_fg_color",
                    "dropdown_hover_color", "width", "height", "font"],
    "CTkSlider": ["command", "width", "height", "progress_color", "button_color", "button_hover_color", "fg_color", "border_width",
                  "border_color", "orientation", "from_", "to", "number_of_steps"],
    "CTkProgressBar": ["fg_color", "progress_color", "border_width", "border_color", "width", "height", "corner_radius"],
    "CTkTextbox": ["fg_color", "border_width", "border_color", "text_color", "width", "height", "font", "wrap"],
    "CTkTabview": ["fg_color", "border_width", "border_color", "width", "height", "text_color", "selected_color", "corner_radius"],
    "CTkSegmentedButton": ["values", "command", "fg_color", "selected_color", "selected_hover_color", "unselected_color", "hover_color",
                           "text_color", "textvariable", "corner_radius", "width", "height", "border_width", "border_color"],
    "CTkSwitch": ["text", "command", "textvariable", "onvalue", "offvalue", "fg_color", "progress_color", "text_color",
                  "width", "height", "border_width", "border_color"],
    "CTkFrame": ["fg_color", "bg_color", "height", "width", "border_width", "border_color"]
}

compound = ["no", "top", "bottom", "left", "right", "top-left", "top-right", "bottom-left", "bottom-right"]
anchor = ["n", "ne", "e", "se", "s", "sw", "w", "nw", "center"]

# Variables de estilo para los widgets

BUTTON_STYLE = {
        "fg_color": "#2E2E2E",  # Color de fondo del boton
        "hover_color": "#3A3A3A",  # Color al pasar el raton por encima
        "text_color": "#FFFFFF",  # Color del texto
        "corner_radius": 8,       # Radio de las esquinas
        "border_color": "#5A5A5A",  # Color del borde
        "border_width": 2,        # Ancho del borde
}

widgets = [
            "CTkButton", "CTkLabel", "CTkEntry", "CTkCheckBox",
            "CTkRadioButton", "CTkComboBox", "CTkSlider", "CTkProgressBar",
            "CTkTextbox", "CTkSwitch", "CTkFrame"
        ]

widgets_info = {
    "es":["Un botón que puede ejecutar una acción cuando se hace clic en él.",
    "Un widget para mostrar texto o imágenes.",
    "Un campo de entrada de texto de una sola línea.",
    "Un botón de opción que puede estar marcado o desmarcado.",
    "Un botón de opción que permite seleccionar una opción de un grupo.",
    "Un cuadro combinado que permite seleccionar una opción de una lista desplegable.",
    "Un control deslizante para seleccionar un valor de un rango.",
    "Una barra de progreso que muestra el progreso de una operación.",
    "Un campo de entrada de texto de varias líneas.",
    "Un interruptor que puede estar en estado encendido o apagado.",
    "Un contenedor para agrupar otros widgets."]
    ,
    "en": [
    "A button that can execute an action when clicked.",
    "A widget for displaying text or images.",
    "A single-line text input field.",
    "A check button that can be checked or unchecked.",
    "A radio button that allows selecting one option from a group.",
    "A combo box that allows selecting an option from a dropdown list.",
    "A slider control for selecting a value from a range.",
    "A progress bar that shows the progress of an operation.",
    "A multi-line text input field.",
    "A switch that can be in an on or off state.",
    "A container for grouping other widgets."
]
}

widget_classes = {
            "VirtualWindow": ctk.CTkToplevel,
            "CTkButton": ctk.CTkButton,
            "CTkLabel": ctk.CTkLabel,
            "CTkEntry": ctk.CTkEntry,
            "CTkCheckBox": ctk.CTkCheckBox,
            "CTkRadioButton": ctk.CTkRadioButton,
            "CTkComboBox": ctk.CTkComboBox,
            "CTkSlider": ctk.CTkSlider,
            "CTkProgressBar": ctk.CTkProgressBar,
            "CTkTextbox": ctk.CTkTextbox,
            "CTkTabview": ctk.CTkTabview,
            "CTkSegmentedButton": ctk.CTkSegmentedButton,
            "CTkSwitch": ctk.CTkSwitch,
            "CTkFrame": ctk.CTkFrame,
            "Canvas": ctk.CTkCanvas,
        }

# Commands variables
event_registry = {}

# Variables para los menus de contexto de CTkMenuBar
context_menu_options = [
    {"label": "Copy", "command": None},
    {"label": "Paste", "command": None},
    {"label": "Cut", "command": None},
    {"label": "Delete", "command": lambda: print("Delete")},
]

# 'mark_widget_with_color' variable de control
widget_marked_color = None
color_default = None