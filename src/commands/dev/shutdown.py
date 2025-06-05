import os
from pathlib import Path
from highrise import User
from src.commands.command_base import CommandBase

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):
        shutdown_flag = Path("shutdown.flag")
        shutdown_flag.write_text("Shutdown requested by admin")
        await self.bot.highrise.chat("Bot is shutting down by admin command.")
        os._exit(0)
