"""Main virtual window implementation."""

from objects.window.window_base import WindowBase
from objects.window.window_state import WindowStateMixin 
from objects.window.widget_manager import WidgetManagerMixin
from objects.window.guide_manager import GuideManagerMixin
from objects.window.io_manager import IOManagerMixin

class VirtualWindow(WindowBase, WindowStateMixin, WidgetManagerMixin, 
                   GuideManagerMixin, IOManagerMixin):
    """Main virtual window class combining all functionality."""
    
    def __init__(self, parent, left_sidebar, app, parameters_dict=None, 
                 width=800, height=500):
        super().__init__(parent, left_sidebar, app, parameters_dict, width, height)