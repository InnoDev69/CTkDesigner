from functools import wraps

def translate_widget(key: str):
    """Decorador para traducción automática de widgets"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            from translations.translator_manager import translator
            widget = func(self, *args, **kwargs)
            if hasattr(widget, 'configure'):
                text = translator.get(key)
                widget.configure(text=text)
            return widget
        return wrapper
    return decorator