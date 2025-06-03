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
        # Try to detect if this is a plugin (by file path or class name)
        is_plugin = False
        # Try to get the file path of the class
        file_path = getattr(self, '__module__', None)
        if file_path and ('.plugins.' in file_path or file_path.startswith('plugins.')):
            is_plugin = True
        # If bot has a plugins_config or commands_config dict, use it
        if is_plugin:
            config_db = getattr(bot, "plugins_config", {}).get(self.__class__.__name__.lower(), {})
            if not config_db and hasattr(self, 'name') and self.name:
                config_db = getattr(bot, "plugins_config", {}).get(self.name, {})
        else:
            config_db = getattr(bot, "commands_config", {}).get(self.__class__.__name__.lower(), {})
            if not config_db and hasattr(self, 'name') and self.name:
                config_db = getattr(bot, "commands_config", {}).get(self.name, {})
        # Fallback: try to load config directly from file if not present in bot
        if not config_db:
            config_path = os.path.join(os.path.dirname(__file__), '../../config/plugins.json' if is_plugin else '../../config/commands.json')
            config_path = os.path.normpath(config_path)
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    try:
                        config_data = json.load(f)
                        config_db = config_data.get(self.__class__.__name__.lower(), {})
                        if not config_db and hasattr(self, 'name') and self.name:
                            config_db = config_data.get(self.name, {})
                    except Exception:
                        pass
        for attr in ["name", "description", "aliases", "cooldown", "permissions"]:
            if attr in config_db:
                setattr(self, attr, config_db[attr])

    @abstractmethod
    async def execute(self, user: User, args: list, message: str):
        """
        Execute the command logic.
        Must be implemented by all subclasses.
        """
        pass
