"""Guide management functionality for the virtual window."""

import logging

class GuideManagerMixin:
    """Handles alignment guides and snapping functionality."""
    
    def create_guide_line(self, x1, y1, x2, y2, color):
        """Create a guide line on the canvas."""
        self.guide_canvas.create_line(x1, y1, x2, y2, fill=color, dash=(4, 2), width=1)

    def clear_guides(self):
        """Remove all guide lines from the canvas."""
        self.guide_canvas.delete("all")

    def draw_guides(self, widget, new_x, new_y, show_guides=True, 
                   color_exact="green", color_near="red", 
                   color_between="red", tolerance=5, snap_range=10):
        """Draw alignment guides and handle widget snapping."""
        if not show_guides:
            return

        self.clear_guides()
        
        widget_edges = self._calculate_widget_edges(widget, new_x, new_y)
        
        for child in self.widgets:
            if child == widget:
                continue

            child_edges = self._calculate_widget_edges(
                child, 
                child.winfo_x(), 
                child.winfo_y()
            )

            self._draw_alignment_guides(widget_edges, child_edges, color_exact, 
                                     color_near, color_between, tolerance, snap_range)

        widget.place(x=widget_edges["left"], y=widget_edges["top"])

    def _calculate_widget_edges(self, widget, x, y):
        """Calculate widget edge positions."""
        width = widget.winfo_width()
        height = widget.winfo_height()
        
        return {
            "left": x,
            "right": x + width,
            "top": y,
            "bottom": y + height,
            "center_x": x + width // 2,
            "center_y": y + height // 2
        }

    def _draw_alignment_guides(self, widget_edges, child_edges, 
                             color_exact, color_near, color_between, 
                             tolerance, snap_range):
        """Draw alignment guides between widgets."""
        
        def draw_guide(x1, y1, x2, y2, widget_edge, child_edge):
            exact = widget_edges[widget_edge] == child_edges[child_edge]
            near = abs(widget_edges[widget_edge] - child_edges[child_edge]) <= tolerance
            color = color_exact if exact else color_near if near else None
            
            if color:
                self.create_guide_line(x1, y1, x2, y2, color)
                if abs(widget_edges[widget_edge] - child_edges[child_edge]) <= snap_range:
                    widget_edges[widget_edge] = child_edges[child_edge]

        # Center alignment
        draw_guide(child_edges["center_x"], 0, child_edges["center_x"], 
                  self.winfo_height(), "center_x", "center_x")
        draw_guide(0, child_edges["center_y"], self.winfo_width(), 
                  child_edges["center_y"], "center_y", "center_y")

        # Edge alignment
        draw_guide(child_edges["left"], 0, child_edges["left"], 
                  self.winfo_height(), "left", "left")
        draw_guide(child_edges["right"], 0, child_edges["right"], 
                  self.winfo_height(), "right", "right")
        draw_guide(0, child_edges["top"], self.winfo_width(), 
                  child_edges["top"], "top", "top")
        draw_guide(0, child_edges["bottom"], self.winfo_width(), 
                  child_edges["bottom"], "bottom", "bottom")

        # Guide lines between nearby widgets
        if abs(widget_edges["center_x"] - child_edges["center_x"]) <= tolerance:
            self.create_guide_line(
                child_edges["center_x"], child_edges["top"],
                child_edges["center_x"], widget_edges["bottom"], 
                color_between
            )
        if abs(widget_edges["center_y"] - child_edges["center_y"]) <= tolerance:
            self.create_guide_line(
                child_edges["left"], child_edges["center_y"],
                widget_edges["right"], child_edges["center_y"], 
                color_between
            )