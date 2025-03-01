import customtkinter as ctk
from objects.animation_mixin import AnimationMixin

def create_widget_with_animation(base_class, *args, **kwargs):
    """
    Crea un widget que hereda automáticamente de AnimationMixin.

    :param base_class: Clase base del widget (e.g., CTkButton).
    :param args: Argumentos posicionales para el widget.
    :param kwargs: Argumentos clave para el widget.
    :return: Instancia del widget con AnimationMixin.
    """
    class WidgetWithAnimation(base_class, AnimationMixin):
        def __init__(self, *args, **kwargs):
            base_class.__init__(self, *args, **kwargs)
            AnimationMixin.__init__(self)

    return WidgetWithAnimation(*args, **kwargs)

if __name__ == "__main__":
    app = ctk.CTk()

    button = create_widget_with_animation(ctk.CTkButton, app, text="Animar")
    button.pack(pady=20, padx=20)

    def start_animation():
        button.animate_to("width", 100, 300, 2, lambda: print("Animación completada"))

    button.configure(command=start_animation)

    app.mainloop()