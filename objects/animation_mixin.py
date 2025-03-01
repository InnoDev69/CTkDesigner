import threading
import time
import customtkinter as ctk

class AnimationMixin:
    def __init__(self):
        # Almacena información sobre las animaciones activas
        self._animations = {}

    def animate_to(self, property_name, start_value, end_value, duration, callback=None):
        """
        Anima una propiedad desde un valor inicial hasta un valor final en un tiempo dado.

        :param property_name: Nombre de la propiedad a animar.
        :param start_value: Valor inicial de la animación.
        :param end_value: Valor final de la animación.
        :param duration: Duración de la animación en segundos.
        :param callback: Función opcional que se ejecuta al finalizar la animación.
        """
        if property_name in self._animations:
            self._animations[property_name]['stop'] = True

        animation_thread = threading.Thread(
            target=self._run_animation,
            args=(property_name, start_value, end_value, duration, callback),
            daemon=True
        )
        self._animations[property_name] = {'thread': animation_thread, 'stop': False}
        animation_thread.start()

    def _run_animation(self, property_name, start_value, end_value, duration, callback):
        steps = 60  # Número de pasos en la animación (FPS)
        interval = duration / steps
        delta = (end_value - start_value) / steps

        for step in range(steps):
            if self._animations[property_name]['stop']:
                return

            current_value = start_value + delta * step
            self._apply_property(property_name, current_value)
            time.sleep(interval)

        # Asegurar que el valor final se aplique
        self._apply_property(property_name, end_value)
        if callback:
            callback()

    def _apply_property(self, property_name, value):
        """
        Aplica un valor a una propiedad específica del widget.
        """
        if hasattr(self, property_name):
            setattr(self, property_name, value)
        elif callable(getattr(self, f'set_{property_name}', None)):
            getattr(self, f'set_{property_name}')(value)

    def stop_animation(self, property_name):
        """
        Detiene cualquier animación activa en una propiedad específica.

        :param property_name: Nombre de la propiedad.
        """
        if property_name in self._animations:
            self._animations[property_name]['stop'] = True

    def loop_animation(self, property_name, start_value, end_value, duration, count=None):
        """
        Repite una animación un número de veces o indefinidamente.

        :param property_name: Nombre de la propiedad.
        :param start_value: Valor inicial.
        :param end_value: Valor final.
        :param duration: Duración de cada animación.
        :param count: Número de repeticiones. Si es None, se repite indefinidamente.
        """
        def loop():
            nonlocal count
            while count is None or count > 0:
                self.animate_to(property_name, start_value, end_value, duration)
                time.sleep(duration)  # Espera a que termine la animación
                self.animate_to(property_name, end_value, start_value, duration)
                time.sleep(duration)
                if count:
                    count -= 1

        threading.Thread(target=loop, daemon=True).start()