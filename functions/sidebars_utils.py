import os
import io
import base64
import logging
from PIL import Image
from tkinter import Tk
import customtkinter as ctk
from objects.tooltip import *
from objects.color_picker import ColorPickerApp
from data.variable import *
from functions.translator_manager import *

def clear_widgets(parent):
    """
    Elimina todos los widgets hijos de un contenedor.

    Args:
        parent: El contenedor (frame o ventana) cuyos widgets serán eliminados.
    """
    for child in parent.winfo_children():
        child.destroy()

def update_treeview(tree, widget_hierarchy, widget_tree):
    """Actualiza el esquema del TreeView basado en la jerarquía de widgets."""
    tree.delete(*tree.get_children())
    widget_tree.clear()

    for widget, parent_widget in widget_hierarchy:
        widget_name = widget._name if hasattr(widget, "_name") else widget.__class__.__name__
        widget_id = id(widget)

        if parent_widget:
            parent_id = id(parent_widget)
            parent_tree_id = widget_tree.get(parent_id)
            tree_id = tree.insert(parent_tree_id, "end", text=widget_name)
        else:
            tree_id = tree.insert("", "end", text=widget_name)

        widget_tree[widget_id] = tree_id

def create_property_entry(parent, widget, prop, update_callback, existing_entries=None):
    """Creates or reuses a property entry."""
    try:
        current_value = widget.cget(prop)

        # Verificar si la entrada existente sigue siendo válida
        if existing_entries and prop in existing_entries:
            entry = existing_entries[prop]
            if str(entry) not in parent.winfo_children():
                del existing_entries[prop]
            else:
                try:
                    entry.delete(0, "end")
                    entry.insert(0, str(current_value))
                    return entry
                except Tk.TclError:
                    logging.warning(f"Entrada para '{prop}' no es válida. Creando una nueva.")

        # Crear nueva entrada si no existe o no es válida
        label = ctk.CTkLabel(parent, text=f"{prop.capitalize()}:")
        label.pack()

        if "color" in prop:
            def show_color_picker():
                color_window = ctk.CTkToplevel(parent)
                color_window.title(translator.translate("COLOR_PICKER_TITLE"))
                color_window.resizable(False, False)

                window_width = 400
                window_height = 500
                screen_width = color_window.winfo_screenwidth()
                screen_height = color_window.winfo_screenheight()
                x = (screen_width - window_width) // 2
                y = (screen_height - window_height) // 2
                color_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

                color_picker = ColorPickerApp(color_window, initial_color=entry.cget("text"))
                color_picker.pack(expand=True, fill="both", padx=10, pady=10)

                def on_color_selected():
                    selected_color = color_picker.get_selected_color()
                    entry.configure(fg_color=selected_color)
                    entry.configure(text=selected_color)
                    entry.configure(text_color=selected_color)
                    entry.configure(hover_color=selected_color)
                    update_callback(widget, prop, entry, tooltip)
                    color_window.destroy()

                accept_btn = ctk.CTkButton(
                    color_picker.buttons_frame, 
                    text=translator.translate("COLOR_PICKER_ACCEPT"), 
                    command=on_color_selected,
                    **BUTTON_STYLE
                )
                accept_btn.pack(pady=10)

                color_window.transient(parent)
                color_window.grab_set()
                parent.wait_window(color_window)

            entry = ctk.CTkButton(
                parent,
                text=current_value,
                fg_color=current_value,
                command=show_color_picker
            )
            entry.pack()
            tooltip = CTkToolTip(entry, translator.translate("TOOLTIP_COLOR_INFO"))

            # Actualizar el diccionario de entradas existentes
            if existing_entries is not None:
                existing_entries[prop] = entry

        elif "image" in prop:
            def base64_to_ctkimage(base64_string):
                image_data = base64.b64decode(base64_string)
                image_pil = Image.open(io.BytesIO(image_data))
                return ctk.CTkImage(
                    light_image=image_pil,
                    dark_image=image_pil,
                    size=image_pil.size
                )
            def upload_image():
                try:
                    file_path = ctk.filedialog.askopenfilename(
                        title=translator.translate("IMAGE_SELECT"),
                        filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
                    )
                    if file_path:
                        # Convertir a base64
                        with open(file_path, "rb") as imagefile:
                            image_base64 = base64.b64encode(imagefile.read())
                        
                        # Convertir base64 a imagen PIL
                        image_data = base64.b64decode(image_base64)
                        image_pil = Image.open(io.BytesIO(image_data))
                        
                        # Crear CTkImage
                        ctk_image = ctk.CTkImage(
                            light_image=image_pil,
                            dark_image=image_pil,
                            size=image_pil.size
                        )
                        
                        # Configurar widget y guardar base64
                        widget.configure(image=ctk_image)
                        widget._image_base64 = image_base64
                        widget._image_reference = ctk_image
                        
                        # Actualizar texto del botón
                        entry.configure(text=os.path.basename(file_path))
                        
                except Exception as e:
                    logging.error(f"Error loading image: {e}")
                    tooltip.configure(message=str(e))
                    tooltip.show()
            entry = ctk.CTkButton(parent, text="Subir" if '' else current_value, command=upload_image, **BUTTON_STYLE)
            entry.pack()
            tooltip = CTkToolTip(entry, translator.translate("TOOLTIP_IMAGE_INFO"))

        elif "state" == prop:
            def update_state():
                if entry.get() == 1:
                    widget.configure(state="normal")
                else:
                    widget.configure(state="disabled")
                entry.configure(text=widget.cget("state").capitalize())
                #update_callback(widget, prop, entry, tooltip)
            entry = ctk.CTkSwitch(parent, text=current_value.capitalize(), command=update_state)
            entry.select()
            entry.pack()

        else:
            entry = ctk.CTkEntry(parent)
            entry.insert(0, str(current_value))
            entry.pack()

            tooltip = CTkToolTip(entry, "")
            tooltip.hide()
            entry.bind("<KeyRelease>", lambda event: update_callback(widget, prop, entry, tooltip))

        return entry

    except Exception as e:
        logging.error(f"Error al crear la entrada para '{prop}': {e}")
        return None

def create_property_entries(parent, widget, properties, update_callback, existing_entries=None):
    """Creates or reuses multiple property entries for a widget."""
    entries = {}
    for prop in properties:
        if entry := create_property_entry(
            parent, widget, prop, update_callback, existing_entries
        ):
            entries[prop] = entry
    return entries