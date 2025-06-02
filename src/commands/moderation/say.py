from highrise import User
from config.config import config

COMMAND_NAME = "say"
COMMAND_DESCRIPTION = "Give the bot a prompt to say"
COMMAND_ALIASES = ['speak', 'talk']
COMMAND_COOLDOWN = 1

class Command:
    """
    Command to give the bot a prompt to say.
    """
    def __init__(self, bot):
        """
        Initialize the say command with the bot instance.
        """
        self.bot = bot
        self.name = COMMAND_NAME
        self.description = COMMAND_DESCRIPTION
        self.permissions = ["say"]
        self.aliases = COMMAND_ALIASES
        self.cooldown = COMMAND_COOLDOWN

    async def execute(self, user: User, args: list, message: str):
        """
        Execute the say command.
        
        :param user: The user who issued the command.
        :param args: The arguments passed with the command.
        :param message: The message containing the command.
        """
        prefix = config.prefix
        text = message.replace(f"{prefix}say", "").strip()
        await self.bot.highrise.chat(text)
