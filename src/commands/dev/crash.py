import os
from highrise import User
from src.commands.command_base import CommandBase

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):
        # Permission is now handled in the handler, no need to check here
        await self.bot.highrise.chat("Bot is crashing down by admin command.")
        os._exit(1)
