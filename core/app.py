"""Core module for global application state"""

app = None

def init_app(instance):
    """Initialize global app instance"""
    global app
    app = instance

def get_app():
    """Get global app instance"""
    global app
    return app