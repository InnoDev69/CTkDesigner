"""Base class for the virtual window implementation."""

import customtkinter as ctk
import logging
import tkinter as tk

class WindowBase(ctk.CTkFrame):
    """Base class with core window functionality."""
    
    def __init__(self, parent, left_sidebar, app, parameters_dict=None, width=800, height=500):
        super().__init__(parent, width=int(width), height=int(height), 
                        bg_color="lightgrey", fg_color="white")
        self.left_sidebar = left_sidebar
        self.app = app
        self.clipboard = ''
        self.widgets = []
        self.parameters_dict = parameters_dict
        self._is_hidden = False
        self._original_positions = {}
        
        self.undo_stack = []
        self.redo_stack = []
        
        self.guide_canvas = tk.Canvas(self, width=width, height=height, 
                                    highlightthickness=0)
        self.guide_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        self.pack_propagate(False)
        self._init_widget_interactions()
        
        logging.info(f"VirtualWindow initialized with dimensions {width}x{height}")
        
    def _init_widget_interactions(self):
        """Initialize widget interaction handlers."""
        self.make_widget_selectable(self)
        self.make_widget_selectable(self.guide_canvas)