"""Widget management functionality for the virtual window."""
from data.variable import widget_classes
import logging
from functions.widget_resize import enable_resizable_highlight, remove_remark

class WidgetManagerMixin:
    """Handles widget creation, deletion and interaction."""

    def add_widget(self, widget_type, **kwargs):
        """Add a widget to the virtual window."""
        self.save_state()
        logging.debug(f"Attempting to add widget of type '{widget_type}'")
        
        if widget := self.create_widget(widget_type, **kwargs):
            center_x = self.cget("width") / 2 - widget.cget("width") / 2
            center_y = self.cget("height") / 2 - widget.cget("height") / 2
            self._place_and_setup_widget(widget, center_x, center_y)
            logging.info(f"Widget added: {widget_type} at ({center_x}, {center_y})")
        else:
            logging.warning(f"Failed to add widget of type '{widget_type}'")

    def _place_and_setup_widget(self, widget, x, y):
        """Place widget and setup its interactions."""
        widget.place(x=x, y=y)
        self.make_widget_movable(widget)
        self.make_widget_selectable(widget)
        self.widgets.append(widget)

    def make_widget_movable(self, widget):
        """Make widget movable within the virtual window."""
        def start_move(event):
            widget._drag_start_x = event.x
            widget._drag_start_y = event.y
            self.clear_guides()

        def do_move(event):
            new_x = widget.winfo_x() + event.x - widget._drag_start_x
            new_y = widget.winfo_y() + event.y - widget._drag_start_y
            widget.place(x=new_x, y=new_y)
            
            self.clear_guides()
            self.draw_guides(widget, new_x, new_y)

            if hasattr(self.left_sidebar, 'update_positions'):
                self.left_sidebar.update_positions(new_x, new_y)

        def stop_move(event):
            self.clear_guides()

        widget.bind("<Button-1>", start_move)
        widget.bind("<B1-Motion>", do_move)
        widget.bind("<ButtonRelease-1>", stop_move)

    def create_widget(self, widget_type, save_state=False, **kwargs):
        """Create a widget instance."""
        if save_state:
            self.save_state()
            
        widget_class = widget_classes.get(widget_type)
        if not widget_class:
            logging.error(f"Invalid widget type: '{widget_type}'")
            return None
            
        widget = widget_class(self, **kwargs)
        logging.info(f"Created {widget_type} widget")
        return widget

    def make_widget_selectable(self, widget):
        """Make a widget selectable with right click."""
        try:
            widget.bind("<Button-3>", lambda e: self._on_widget_select(e, widget))
            widget.bind("<Delete>", lambda e: self.left_sidebar.delete_widget(widget))
            widget.bind("<Control-c>", lambda e: self._copy_widget(widget))
            widget.bind("<Control-v>", lambda e: self._paste_widget())
            
            if widget.__class__.__name__ != "Canvas":
                enable_resizable_highlight(self.guide_canvas, widget, self.left_sidebar)
                
            logging.info(f"Made widget selectable: {widget.__class__.__name__}")
            
        except Exception as e:
            logging.error(f"Widget selection error: {e}")

    def _on_widget_select(self, event, widget):
        """Handle widget selection."""
        logging.info(f"{widget.__class__.__name__} selected.")
        if widget.__class__.__name__ == "Canvas":
            self.left_sidebar.show_widget_config(self)
            widget.bind("<Button-3>", lambda e: self._on_widget_select(e, widget))
        else:
            self.left_sidebar.show_widget_config(widget)
            enable_resizable_highlight(self.guide_canvas, widget, self.left_sidebar)

    def _copy_widget(self, widget):
        """Copy a widget to clipboard."""
        self.clipboard = widget
        logging.info(f"{widget.__class__.__name__} copied.")

    def _paste_widget(self):
        """Paste widget from clipboard."""
        if self.clipboard:
            self.app.inter_add_widget(self.clipboard)
            logging.info(f"{self.clipboard.__class__.__name__} pasted.")
        else:
            logging.info("No widget selected to paste.")

    def delete_widget(self, widget):
        """Delete a widget."""
        remove_remark(self.guide_canvas, widget)
        self.save_state()
        widget.destroy()
        self.widgets.remove(widget)
        logging.debug(f"Deleted widget: {widget}")

    def create_and_place_widget(self, widget_type, properties, x, y, save_state=True):
        """Create and place a widget with given properties at specified position."""
        if save_state:
            self.save_state()
            
        logging.debug(f"Creating and placing widget of type '{widget_type}'")
        
        if widget := self.create_widget(widget_type, **properties):
            self._place_and_setup_widget(widget, x, y)
            logging.info(f"Widget placed: {widget_type} at ({x}, {y})")
            return widget
        return None