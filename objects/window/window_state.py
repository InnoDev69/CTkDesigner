"""State management functionality for the virtual window."""
from data.variable import global_properties
class WindowStateMixin:
    """Handles undo/redo and widget state management."""

    def save_state(self):
        """Save current state to undo stack and clear redo."""
        self.undo_stack.append(self.get_current_state())
        self.redo_stack.clear()

    def undo(self):
        """Undo last action."""
        if not self.undo_stack:
            print("No actions to undo.")
            return
        self.redo_stack.append(self.get_current_state())
        last_state = self.undo_stack.pop()
        self.restore_state(last_state)

    def redo(self):
        """Redo last undone action."""
        if not self.redo_stack:
            print("No actions to redo.")
            return
        self.undo_stack.append(self.get_current_state())
        next_state = self.redo_stack.pop()
        self.restore_state(next_state)

    def get_current_state(self):
        """Get current window state."""
        return [{
            "type": widget.__class__.__name__,
            "properties": {
                prop: widget.cget(prop) 
                for prop in global_properties.get(widget.__class__.__name__, [])
            },
            "x": widget.winfo_x(),
            "y": widget.winfo_y()
        } for widget in self.widgets]

    def restore_state(self, state):
        """Restore window to a saved state."""
        self.clean_virtual_window(save_state=False)
        for widget_data in state:
            self.create_and_place_widget(
                widget_data["type"],
                widget_data["properties"],
                widget_data["x"],
                widget_data["y"],
                save_state=False
            )