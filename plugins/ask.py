import logging

from config.config import config
from highrise import User
from src.commands.command_base import CommandBase
from src.utility.ai import chat

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
            await self.bot.highrise.chat(self.get_setting("response_thinking_message", "\n 🤔"))
            response = chat(f"You can currently see these people {users}. And you can there also see their IDs, usernames and coordinates in this room. This prompt was asked by: {user.username}. {question}. On this question you MUST DIRECTLY ANSWER!")
            await self.bot.highrise.chat(f"\n{response.strip()}")
        except Exception as e:
            await self.bot.highrise.chat(self.get_setting("error_message", "Sorry, something went wrong with the AI response."))
            logging.error(f"Error in ask command: {e}", exc_info=True)

    def on_chat_handler(self, user, message):
        print(f"DEBUG: on_chat_handler called with message: {message}")
        prefix = config.prefix
        # Only respond if not a direct command call (e.g., !ask ...)
        if message.strip().lower().startswith(f"{prefix}{self.name}"):
            return
        words = set(message.lower().split())
        if "seb" in words or "sebastian" in words:
            args = message.split()
            import asyncio
            asyncio.create_task(self.execute(user, args, message))