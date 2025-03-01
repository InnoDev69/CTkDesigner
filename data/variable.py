import customtkinter as ctk

global_properties = {
    "VirtualWindow": ["width", "height", "fg_color", "bg_color", "border_width", "border_color"],
    "CTkButton": ["text", "command", "fg_color", "width", "height", "border_width", "border_color", "hover_color", "text_color",
                  "border_spacing", "corner_radius"],
    "CTkLabel": ["text", "textvariable", "fg_color", "corner_radius", "text_color", "width", "height", "font", "anchor", "compound",
                 "justify"],
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