from abc import ABC, abstractmethod
from highrise import User
import os
import json

class CommandBase(ABC):
    """
    Abstract base class for all commands.
    Enforces a consistent interface and structure.
    Automatically loads config from commands.json or plugins.json if available.
    """
    def __init__(self, bot):
        self.bot = bot
        # Default values
        self.name = None
        self.description = None
        self.aliases = []
        self.cooldown = 0
        self.permissions = []
        # Determine config source: plugin or command
        config_db = {}
        is_plugin = False
        file_path = getattr(self, '__module__', None)
        if file_path and ('.plugins.' in file_path or file_path.startswith('plugins.')):
            is_plugin = True
        # Try to get the plugin name from the module path (filename)
        plugin_name = None
        if is_plugin and file_path:
            # plugins.dummy or plugins.ask
            plugin_name = file_path.split('.')[-1]
        if is_plugin:
            # Load config from plugins.json if available
            config_db = getattr(bot, "plugins_config", {}).get(plugin_name, {})
            if not config_db and hasattr(self, 'name') and self.name:
                config_db = getattr(bot, "plugins_config", {}).get(self.name, {})
            if not config_db:
                config_path = os.path.join(os.path.dirname(__file__), '../../config/plugins.json')
                config_path = os.path.normpath(config_path)
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        try:
                            config_data = json.load(f)
                            config_db = config_data.get(plugin_name, {})
                            if not config_db and hasattr(self, 'name') and self.name:
                                config_db = config_data.get(self.name, {})
                        except Exception:
                            pass
        else:
            config_db = getattr(bot, "commands_config", {}).get(self.__class__.__name__.lower(), {})
            if not config_db and hasattr(self, 'name') and self.name:
                config_db = getattr(bot, "commands_config", {}).get(self.name, {})
        for attr in ["name", "description", "aliases", "cooldown", "permissions"]:
            if attr in config_db:
                setattr(self, attr, config_db[attr])
        # Fallback: set name to plugin_name if not set
        if is_plugin and not self.name and plugin_name:
            self.name = plugin_name
        self.handlers = {}

    def add_handler(self, event_name, func):
        """
        Register a custom event handler for the command.
        """
        if event_name not in self.handlers:
            self.handlers[event_name] = []
        self.handlers[event_name].append(func)

    def get_handlers(self, event_name):
        """
        Retrieve registered event handlers for the command.
        """
        return self.handlers.get(event_name, [])

    @abstractmethod
    async def execute(self, user: User, args: list, message: str):
        """
        Execute the command logic.
        Must be implemented by all subclasses.
        """
        pass
