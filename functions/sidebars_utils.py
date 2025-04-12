import logging
import customtkinter as ctk
from objects.tooltip import *

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
    """Crea o reutiliza una entrada de propiedad para un widget."""
    try:
        current_value = widget.cget(prop)

        # Verificar si la entrada existente sigue siendo válida
        if existing_entries and prop in existing_entries:
            entry = existing_entries[prop]
            if str(entry) not in parent.winfo_children():
                # Si el widget no es válido, elimina la referencia
                del existing_entries[prop]
            else:
                try:
                    entry.delete(0, "end")  # Verifica si el widget aún existe
                    entry.insert(0, str(current_value))
                    return entry
                except ctk.TclError:
                    # Si el widget no es válido, crea uno nuevo
                    logging.warning(f"Entrada para '{prop}' no es válida. Creando una nueva.")

        # Crear nueva entrada si no existe o no es válida
        label = ctk.CTkLabel(parent, text=f"{prop.capitalize()}:")
        label.pack()
        entry = ctk.CTkEntry(parent)
        entry.insert(0, str(current_value))
        entry.pack()

        tooltip = CTkToolTip(entry, "")
        tooltip.hide()
        entry.bind("<KeyRelease>", lambda event: update_callback(widget, prop, entry, tooltip))

        # Actualizar el diccionario de entradas existentes
        if existing_entries is not None:
            existing_entries[prop] = entry

        return entry
    except Exception as e:
        logging.error(f"Error al crear la entrada para '{prop}': {e}")

def create_property_entries(parent, widget, properties, update_callback, existing_entries=None):
    """Crea o reutiliza múltiples entradas de propiedad para un widget."""
    entries = {}
    for prop in properties:
        entries[prop] = create_property_entry(parent, widget, prop, update_callback, existing_entries)
    return entries