from highrise import User
from config.config import config
from src.utility.ai import chat
from src.commands.command_base import CommandBase
import logging

class Command(CommandBase):
    """
    Command to ask the AI a question and get a response.
    """
    def __init__(self, bot):
        super().__init__(bot)

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
            question = message.replace(f"{prefix}{self.name}", "").strip()
            await self.bot.highrise.chat("\n 🤔")
            response = chat(f"You can currently see these people {users}. And you can there also see their IDs, usernames and coordinates in this room. This prompt was asked by: {user.username}. {question}. On this question you MUST DIRECTLY ANSWER!")
            await self.bot.highrise.chat(f"\n{response.strip()}")
        except Exception as e:
            await self.bot.highrise.chat("Sorry, something went wrong with the AI response.")
            logging.error(f"Error in ask command: {e}", exc_info=True)
