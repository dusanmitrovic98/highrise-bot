from abc import ABC, abstractmethod
from highrise import User

class CommandBase(ABC):
    """
    Abstract base class for all commands.
    Enforces a consistent interface and structure.
    """
    def __init__(self, bot):
        self.bot = bot
        self.name = None
        self.description = None
        self.aliases = []
        self.cooldown = 0
        self.permissions = []

    @abstractmethod
    async def execute(self, user: User, args: list, message: str):
        """
        Execute the command logic.
        Must be implemented by all subclasses.
        """
        pass
