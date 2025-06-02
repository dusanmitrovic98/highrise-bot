from highrise import User
from config.config import config
from src.utility.ai import ask_bot

COMMAND_NAME = "allow_to_roam"
DESCRIPTION = "Allows the bot to roam."
PERMISSIONS = ["allow_to_roam"]
ALIASES = ['speak', 'talk']
COOLDOWN = 10

class Command:
    """
    Command to allow or disallow the bot to roam freely.
    """
    def __init__(self, bot):
        """
        Initialize the command with the bot instance.
        """
        self.bot = bot
        self.name = COMMAND_NAME
        self.description = DESCRIPTION
        self.permissions = PERMISSIONS
        self.aliases = ALIASES
        self.cooldown = COOLDOWN

    async def execute(self, user: User, args: list, message: str):
        """
        Execute the command to allow or disallow the bot to roam freely.
        
        :param user: The user who issued the command.
        :param args: The arguments passed with the command.
        :param message: The message containing the command.
        """
        prefix = config.prefix
        command = message.replace(f"{prefix}{COMMAND_NAME}", "").strip()

        if command == "yes":
            await self.set_roam_status(True, user)
        elif command == "no":
            await self.set_roam_status(False, user)

    async def set_roam_status(self, status: bool, user: User):
        """
        Set the roam status of the bot and send a response message.
        
        :param status: The new roam status.
        :param user: The user who issued the command.
        """
        config.allowed_to_roam = status
        question = "I just allowed you to walk freely what do you say on that?" if status else "I just forbid you to walk freely what do you say on that?"
        await ask_bot(self.bot, user, question)
