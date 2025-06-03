from abc import ABC, abstractmethod
from highrise import User

class CommandBase(ABC):
    """
    Abstract base class for all commands.
    Enforces a consistent interface and structure.
    Automatically loads config from commands.json if available.
    """
    def __init__(self, bot):
        self.bot = bot
        # Default values
        self.name = None
        self.description = None
        self.aliases = []
        self.cooldown = 0
        self.permissions = []
        # Load config from commands.json if available
        config_db = getattr(bot, "commands_config", {}).get(self.__class__.__name__.lower(), {})
        # Fallback: try by file/command name if not found by class name
        if not config_db and hasattr(self, 'name') and self.name:
            config_db = getattr(bot, "commands_config", {}).get(self.name, {})
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
