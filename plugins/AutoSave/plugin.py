import time
import json
import logging
import customtkinter as CTk
from pathlib import Path
from plugins.plugin_manager import Plugin

class Plugin(Plugin):
    def __init__(self):
        self.name = "AutoSave Plugin"
        self.version = "1.0.2"
        self.description = "Auto-guarda el proyecto cada cierto tiempo"
        self.author = "Innodev69"
        
        # Ruta del archivo de configuración
        self.config_path = Path("plugins/AutoSave/config.json")
        
        # Valores por defecto
        self.default_config = {
            "save_interval": 5 * 60,  # 5 minutos
            "max_saves": 5
        }
        
        # Cargar configuración
        self.load_config()
        
        self.last_save = time.time()
        self.config_window = None

    def load_config(self):
        """Carga la configuración desde el archivo JSON"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                self.save_interval = config.get('save_interval', self.default_config['save_interval'])
                self.max_saves = config.get('max_saves', self.default_config['max_saves'])
            else:
                # Usar valores por defecto si no existe el archivo
                self.save_interval = self.default_config['save_interval']
                self.max_saves = self.default_config['max_saves']
                # Crear el archivo de configuración con valores por defecto
                self.save_config_to_file()
        except Exception as e:
            logging.error(f"Error cargando configuración: {e}")
            # Usar valores por defecto en caso de error
            self.save_interval = self.default_config['save_interval']
            self.max_saves = self.default_config['max_saves']

    def save_config_to_file(self):
        """Guarda la configuración en el archivo JSON"""
        try:
            # Asegurar que el directorio existe
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            config = {
                'save_interval': self.save_interval,
                'max_saves': self.max_saves
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
                
        except Exception as e:
            logging.error(f"Error guardando configuración: {e}")

    def on_initialize(self) -> None:
        """Inicializa el plugin y configura el timer de auto-guardado"""
        print("Inicializando AutoSave Plugin")
        self.app.plugin_button_drop.add_separator()
        self.app.plugin_button_drop.add_option("Autosave plugin configuration", self.open_config_window)
        self.app.menu_button_drop.add_separator()
        submenu=self.app.menu_button_drop.add_submenu("Autosave", 3)
        if files:= self.get_autosave_files():
            for path in files:
                submenu.add_option(path.name, lambda p=path: self.app.virtual_window.import_from_json(str(p)))
        else:
            submenu.add_option("No hay auto-guardados disponibles", None, state="disabled")
        self._schedule_autosave()

    def open_config_window(self):
        """Abre la ventana de configuración del plugin"""
        if self.config_window is not None and self.config_window.winfo_exists():
            return
        self.config_window = CTk.CTkToplevel(self.app)
        self.config_window.title("Configuración de AutoSave Plugin")
        self.config_window.geometry("400x300")
        self.config_window.resizable(False, False)

        # Frame principal
        main_frame = CTk.CTkFrame(self.config_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title = CTk.CTkLabel(
            main_frame, 
            text="Configuración de Auto-guardado",
            font=("Helvetica", 16, "bold")
        )
        title.pack(pady=(0, 20))

        # Tiempo restante para próximo autosave
        self.time_remaining_frame = CTk.CTkFrame(main_frame)
        self.time_remaining_frame.pack(fill="x", pady=(0, 20))
        
        time_remaining_label = CTk.CTkLabel(
            self.time_remaining_frame,
            text="Próximo autosave en:",
            font=("Helvetica", 12)
        )
        time_remaining_label.pack(side="left", padx=5)
        
        self.countdown_label = CTk.CTkLabel(
            self.time_remaining_frame,
            text="00:00",
            font=("Helvetica", 12, "bold")
        )
        self.countdown_label.pack(side="right", padx=5)
        
        # Iniciar actualización del contador
        self._update_countdown()

        interval_frame = self._extracted_from_open_config_window_22(
            main_frame, 10, "Intervalo de guardado (minutos):"
        )
        self.interval_var = CTk.StringVar(value=str(self.save_interval // 60))
        interval_entry = CTk.CTkEntry(
            interval_frame,
            textvariable=self.interval_var,
            width=100
        )
        interval_entry.pack(side="right", padx=5)

        max_saves_frame = self._extracted_from_open_config_window_22(
            main_frame, 20, "Número máximo de auto-guardados:"
        )
        self.max_saves_var = CTk.StringVar(value=str(self.max_saves))
        max_saves_entry = CTk.CTkEntry(
            max_saves_frame,
            textvariable=self.max_saves_var,
            width=100
        )
        max_saves_entry.pack(side="right", padx=5)

        # Ubicación actual de guardado
        save_location = CTk.CTkLabel(
            main_frame,
            text=f"Ubicación: {Path('autosaves').absolute()}",
            wraplength=350
        )
        save_location.pack(pady=(0, 20))

        # Botones
        button_frame = CTk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))

        save_button = CTk.CTkButton(
            button_frame,
            text="Guardar",
            command=self._save_config
        )
        save_button.pack(side="left", padx=5, expand=True)

        cancel_button = CTk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.config_window.destroy
        )
        cancel_button.pack(side="right", padx=5, expand=True)

    # TODO Rename this here and in `open_config_window`
    def _extracted_from_open_config_window_22(self, main_frame, arg1, text):
            # Intervalo de guardado
        result = CTk.CTkFrame(main_frame)
        result.pack(fill="x", pady=(0, arg1))

        interval_label = CTk.CTkLabel(result, text=text)
        interval_label.pack(side="left", padx=5)

        return result

    def _schedule_autosave(self):
        """Programa el siguiente auto-guardado"""
        current_time = time.time()
        if current_time - self.last_save >= self.save_interval:
            self._perform_autosave()
            self.last_save = current_time
            
        # Programa el siguiente chequeo
        self.app.after(1000, self._schedule_autosave)
        
    def _perform_autosave(self):
        """Realiza el auto-guardado"""
        try:
            autosave_dir = Path("autosaves")
            autosave_dir.mkdir(exist_ok=True)
            
            filename = f"autosave_{int(time.time())}.json"
            filepath = autosave_dir / filename
            
            self.app.virtual_window.export_to_json(str(filepath))
            self.app.cross_update_text_info(f"Auto-guardado completado: {filename}")
            
            # Mantener solo los últimos 5 auto-guardados
            self._cleanup_old_autosaves()
        
        except Exception as e:
            logging.error(f"Error en auto-guardado: {e}")

    def get_autosave_files(self) -> list[Path]:
        """Obtiene la lista de archivos autoguardados ordenados por fecha.
        
        Returns:
            list[Path]: Lista de rutas de archivos autoguardados ordenados del más reciente al más antiguo
        """
        try:
            autosave_dir = Path("autosaves")
            if not autosave_dir.exists():
                return []

            return sorted(
                autosave_dir.glob("autosave_*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True,  # Más reciente primero
            )
        except Exception as e:
            print(f"Error obteniendo lista de autoguardados: {e}")
            return []
    
    def _cleanup_old_autosaves(self):
        """Limpia auto-guardados antiguos"""
        autosave_dir = Path("autosaves")
        files = sorted(autosave_dir.glob("autosave_*.json"))
        
        while len(files) > 5:
            files[0].unlink()
            files = files[1:]
            
    def cleanup(self) -> None:
        """Limpieza al desactivar el plugin"""
        # Guardar configuración actual antes de desactivar
        self.save_config_to_file()
        logging.info("Desactivando AutoSave Plugin")
        
    def _save_config(self):
        """Guarda los cambios de la configuración"""
        try:
            # Obtener y validar nuevos valores
            new_interval = int(self.interval_var.get())
            new_max_saves = int(self.max_saves_var.get())
            
            if new_interval <= 0 or new_max_saves <= 0:
                CTk.CTkMessagebox(
                    title="Error",
                    message="Los valores deben ser mayores que 0",
                    icon="cancel"
                )
                return
                
            # Actualizar valores en el objeto
            self.save_interval = new_interval * 60  # Convertir minutos a segundos
            self.max_saves = new_max_saves
            
            # Reiniciar el tiempo del último guardado para que el contador comience desde el nuevo intervalo
            self.last_save = time.time()
            
            # Guardar en el archivo JSON
            self.save_config_to_file()
            
            # Cerrar ventana y mostrar mensaje de éxito
            self.config_window.destroy()
            self.app.cross_update_text_info("Configuración guardada correctamente")
            
        except ValueError:
            CTk.CTkMessagebox(
                title="Error",
                message="Por favor ingrese valores numéricos válidos",
                icon="cancel"
            )

    def _format_time_remaining(self, seconds):
        """Formatea el tiempo restante en formato mm:ss"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def _update_countdown(self):
        """Actualiza el contador de tiempo restante"""
        if hasattr(self, 'config_window') and self.config_window.winfo_exists():
            current_time = time.time()
            time_elapsed = current_time - self.last_save
            time_remaining = max(0, self.save_interval - time_elapsed)
            
            self.countdown_label.configure(
                text=self._format_time_remaining(time_remaining)
            )
            
            # Actualizar cada segundo
            self.config_window.after(1000, self._update_countdown)