import os
import sys
import json
import importlib.util
from plugins.plugin_logger import PluginLogger
from core.logging import logger
from pathlib import Path
from typing import Dict, List, Any, Optional

class Plugin:
    """Base class for plugins"""
    def __init__(self):
        self.name = "Base Plugin"
        self.version = "1.0.0"
        self.description = "Base plugin class"
        self.author = "Yo"
        self.logger = PluginLogger(self.name)
        
    def initialize(self, app) -> None:
        """Initialize plugin with retry mechanism.
        
        Args:
            app: The main application instance
        """
        self.app = app
        
        try:
            try:    
                self.on_initialize(app)
            except TypeError:
                self.on_initialize()
            
            self.logger.info(f"Plugin '{self.name}' initialized successfully.")
            self.logger.lifecycle("Initialized")
            return True
                    
        except AttributeError as e:
            self.logger.error(f"Plugin '{self.name}' initialization failed: {e}")
        
    def on_initialize(self) -> None:
        """Override this method in child plugins to implement initialization logic"""
        pass
        
    def cleanup(self) -> None:
        """Cleanup when plugin is disabled"""
        self.logger.lifecycle("cleanup started")
        # Override en plugins hijos
        self.logger.lifecycle("cleanup completed")
        
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
                logger.error(f"Error loading plugin config: {e}")
                self.enabled_plugins = {}
                
    def _save_plugin_config(self) -> None:
        """Save plugin configuration to JSON"""
        config_path = Path(__file__).parent / "plugin_config.json"
        try:
            with open(config_path, "w") as f:
                json.dump(self.enabled_plugins, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving plugin config: {e}")
                
    def discover_plugins(self) -> None:
        """Discover available plugins in plugins directory"""
        plugin_dir = Path(__file__).parent
        for plugin_path in plugin_dir.glob("*/plugin.py"):
            try:
                self._load_plugin(plugin_path)
            except Exception as e:
                self.logger.error(f"Error loading plugin {plugin_path}: {e}")
                
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
            logger.error(f"Error loading plugin {plugin_path}: {e}")
            
    def initialize_plugins(self, app) -> None:
        """Initialize all enabled plugins"""
        for name, plugin in self.plugins.items():
            if self.enabled_plugins.get(name, True):
                try:
                    plugin.initialize(app)
                    logger.info(f"Initialized plugin: {name}")
                except Exception as e:
                    logger.error(f"Error initializing plugin {name}: {e}")
                    
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