from highrise import User
from config.config import config
from src.utility.ai import chat
from src.commands.command_base import CommandBase
import logging
import re

class Command(CommandBase):
    """
    Command to ask the AI a question and get a response.
    """
    def __init__(self, bot):
        super().__init__(bot)
        self.add_handler("on_chat", self.on_chat_handler)

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
            # Normalize whitespace: replace multiple spaces (or any whitespace) with a single space
            response = re.sub(r'\s+', ' ', response)
            await self.bot.highrise.chat(f"\n{response.strip()}")
        except Exception as e:
            await self.bot.highrise.chat("Sorry, something went wrong with the AI response.")
            logging.error(f"Error in ask command: {e}", exc_info=True)

    async def on_chat_handler(self, user, message):
        print(f"DEBUG: on_chat_handler called with message: {message}")
        if "seb" in message.lower() or "sebastian" in message.lower():
            args = message.split()
            await self.execute(user, args, message)