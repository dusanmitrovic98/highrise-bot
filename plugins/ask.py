from highrise import User
from config.config import config
from src.utility.ai import ask_bot, chat

COMMAND_NAME = "ask"
DESCRIPTION = "Give the AI the question to answer"
PERMISSIONS = ["ask"]
ALIASES = ['speak', 'talk']
COOLDOWN = 10

class Command:
    """
    Command to ask the AI a question and get a response.
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
        Execute the command to get a response from the AI.
        :param user: The user who issued the command.
        :param args: The arguments passed with the command.
        :param message: The message containing the command.
        """
        try:
            users = await self.bot.highrise.get_room_users()
            users = users.content
            prefix = config.prefix
            question = message.replace(f"{prefix}{COMMAND_NAME}", "").strip()
            await self.bot.highrise.chat("\n 🤔")
            response = chat(f"You can currently see these people {users}. And you can there also see their IDs, usernames and coordinates in this room. This prompt was asked by: {user.username}. {question}. On this question you MUST DIRECTLY ANSWER!")
            await self.bot.highrise.chat(f"\n{response}")
        except Exception as e:
            await self.bot.highrise.chat("Sorry, something went wrong with the AI response.")
            # Optionally log the error
