import importlib
import os


class PluginManager:
    def __init__(self, app, plugin_folder='src/plugins'):
        self.app = app
        self.plugin_folder = plugin_folder
        self.plugins = {}

    def load_plugins(self, plugin_folder='src/plugins'):
        for plugin_name in os.listdir(plugin_folder):
            plugin_path = os.path.join(plugin_folder, plugin_name)
            if os.path.isdir(plugin_path) and '__init__.py' in os.listdir(plugin_path):
                module_name = f"src.plugins.{plugin_name}"
                module = importlib.import_module(module_name)
                if hasattr(module, 'create_plugin'):
                    plugin_instance = module.create_plugin(self.app)
                    plugin_instance.init_app()

    def load_plugin(self, plugin_name):
        plugin_path = os.path.join(self.plugin_folder, plugin_name)
        if os.path.isdir(plugin_path) and '__init__.py' in os.listdir(plugin_path):
            module_name = f"{self.plugin_folder}.{plugin_name}".replace('/', '.')
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, 'create_plugin'):
                    plugin_instance = module.create_plugin(self.app)
                    plugin_instance.init_app()
                    self.plugins[plugin_name] = plugin_instance
                    print(f"Loaded plugin: {plugin_name}")
                else:
                    print(f"No create_plugin function found in {plugin_name}")
            except Exception as e:
                print(f"Error loading plugin {plugin_name}: {e}")
        else:
            print(f"Skipping {plugin_name}, not a valid plugin directory")

    def unload_plugin(self, plugin_name):
        if plugin_name in self.plugins:
            plugin_instance = self.plugins.pop(plugin_name)
            if hasattr(plugin_instance, 'teardown'):
                plugin_instance.teardown()
            print(f"Unloaded plugin: {plugin_name}")
        else:
            print(f"Plugin {plugin_name} not loaded")

    def reload_plugin(self, plugin_name):
        self.unload_plugin(plugin_name)
        self.load_plugin(plugin_name)