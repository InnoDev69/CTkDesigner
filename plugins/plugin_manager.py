import os
import sys
import json
import logging
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional

class Plugin:
    """Base class for plugins"""
    def __init__(self):
        self.name = "Base Plugin"
        self.version = "1.0.0"
        self.description = "Base plugin class"
        self.author = "Yo"
        
    def initialize(self, app, retries=100, delay=5000) -> None:
        """Initialize plugin with retry mechanism.
        
        Args:
            app: The main application instance
            retries (int): Number of retry attempts (default: 3)
            delay (int): Delay between retries in milliseconds (default: 1000)
        """
        self.app = app
        
        def attempt_initialize(remaining_retries):
            try:
                if hasattr(self.app, 'toolbar') and self.app.toolbar:
                    try:    
                        self.on_initialize(app)
                    except TypeError:
                        self.on_initialize()
                    print(f"Plugin '{self.name}' initialized successfully.")
                    self.app.cross_update_text_info(
                        f"Plugin '{self.name}' initialized successfully."
                    )
                    return True
                else:
                    print(f"Plugin '{self.name}' waiting for toolbar. Attempts left: {remaining_retries}")
                    if remaining_retries > 0:
                        self.app.after(delay, lambda: attempt_initialize(remaining_retries - 1))
                    return False
                    
            except AttributeError as e:
                print(f"Plugin '{self.name}' initialization failed: {e}")
                if remaining_retries > 0:
                    self.app.after(delay, lambda: attempt_initialize(remaining_retries - 1))
                return False

        attempt_initialize(retries)
        
    def on_initialize(self) -> None:
        """Override this method in child plugins to implement initialization logic"""
        pass
        
    def cleanup(self) -> None:
        """Cleanup when plugin is disabled"""
        pass
        
class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.enabled_plugins: Dict[str, bool] = {}
        self._load_plugin_config()
        
    def _load_plugin_config(self) -> None:
        """Load plugin configuration from JSON"""
        config_path = Path(__file__).parent / "plugin_config.json"
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    self.enabled_plugins = json.load(f)
            except Exception as e:
                print(f"Error loading plugin config: {e}")
                self.enabled_plugins = {}
                
    def _save_plugin_config(self) -> None:
        """Save plugin configuration to JSON"""
        config_path = Path(__file__).parent / "plugin_config.json"
        try:
            with open(config_path, "w") as f:
                json.dump(self.enabled_plugins, f, indent=2)
        except Exception as e:
            print(f"Error saving plugin config: {e}")
                
    def discover_plugins(self) -> None:
        """Discover available plugins in plugins directory"""
        plugin_dir = Path(__file__).parent
        for plugin_path in plugin_dir.glob("*/plugin.py"):
            try:
                self._load_plugin(plugin_path)
            except Exception as e:
                logging.error(f"Error loading plugin {plugin_path}: {e}")
                
    def _load_plugin(self, plugin_path: Path) -> None:
        """Load a single plugin from path"""
        try:
            spec = importlib.util.spec_from_file_location(
                f"plugin_{plugin_path.parent.name}",
                plugin_path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            
            plugin_class = getattr(module, "Plugin", None)
            if plugin_class and issubclass(plugin_class, Plugin):
                plugin = plugin_class()
                self.plugins[plugin.name] = plugin
                if plugin.name not in self.enabled_plugins:
                    self.enabled_plugins[plugin.name] = True
                    
        except Exception as e:
            print(f"Error loading plugin {plugin_path}: {e}")
            
    def initialize_plugins(self, app) -> None:
        """Initialize all enabled plugins"""
        for name, plugin in self.plugins.items():
            if self.enabled_plugins.get(name, True):
                try:
                    plugin.initialize(app)
                    print(f"Initialized plugin: {name}")
                except Exception as e:
                    print(f"Error initializing plugin {name}: {e}")
                    
    def enable_plugin(self, name: str) -> None:
        """Enable a plugin"""
        if name in self.plugins:
            self.enabled_plugins[name] = True
            self._save_plugin_config()
            
    def disable_plugin(self, name: str) -> None:
        """Disable a plugin"""
        if name in self.plugins:
            self.enabled_plugins[name] = False
            if plugin := self.plugins[name]:
                plugin.cleanup()
            self._save_plugin_config()